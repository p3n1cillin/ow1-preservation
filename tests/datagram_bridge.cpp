#include "tools/offline-launch/loopback_bridge.h"
#include <array>

int main() {
    using namespace loopback_bridge;
    WSADATA wsa{};
    if (WSAStartup(MAKEWORD(2,2), &wsa)) return 1;
    auto bound_socket = []() {
        auto s = datagram_socket(); auto address = loopback_address(0);
        if (bind(s, reinterpret_cast<sockaddr*>(&address), sizeof(address))) throw std::runtime_error("test bind");
        DWORD timeout = 2000;
        setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<char*>(&timeout), sizeof(timeout));
        return s;
    };
    auto address_of = [](SOCKET s) {
        sockaddr_in address{}; int size = sizeof(address);
        if (getsockname(s, reinterpret_cast<sockaddr*>(&address), &size)) throw std::runtime_error("test address");
        return address;
    };
    HANDLE server = INVALID_HANDLE_VALUE, client = INVALID_HANDLE_VALUE;
    SOCKET inside = INVALID_SOCKET, outside = INVALID_SOCKET, sender = INVALID_SOCKET, receiver = INVALID_SOCKET;
    std::atomic<bool> stop{false}; std::thread a, b;
    uint64_t ap=0,as=0,bp=0,bs=0;
    int result = 0;
    try {
        const auto name = pipe_name(GetCurrentProcessId(), 1, true) + L"-fixture";
        server = CreateNamedPipeW(name.c_str(), PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED | FILE_FLAG_FIRST_PIPE_INSTANCE,
            PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS, 1, 8192, 8192, 0, nullptr);
        if (server == INVALID_HANDLE_VALUE) throw std::runtime_error("test pipe");
        OVERLAPPED operation{}; operation.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        ConnectNamedPipe(server, &operation);
        client = CreateFileW(name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, nullptr);
        DWORD ignored;
        const bool connected = GetOverlappedResult(server, &operation, &ignored, TRUE) != FALSE;
        CloseHandle(operation.hEvent);
        if (client == INVALID_HANDLE_VALUE || !connected) throw std::runtime_error("test pipe connection");
        inside = bound_socket(); receiver = bound_socket(); sender = bound_socket(); outside = datagram_socket();
        const auto destination = address_of(receiver), input = address_of(inside);
        if (connect(outside, reinterpret_cast<const sockaddr*>(&destination), sizeof(destination))) throw std::runtime_error("test connect");
        a = std::thread([&]() { pump_datagrams(client, inside, true, ap, as, &stop); });
        b = std::thread([&]() { pump_datagrams(server, outside, false, bp, bs, &stop); });
        // Author-written payloads: exercise zero-length, embedded NUL and the
        // datagram limit in both directions, without concatenation or truncation.
        for (const int size : {0, 1, 33, 4096}) {
            std::array<char,4096> sent{}, received{};
            for (int i=0;i<size;++i) sent[i] = static_cast<char>((i*17+size)&255);
            if (sendto(sender, sent.data(), size, 0, reinterpret_cast<const sockaddr*>(&input), sizeof(input)) != size)
                throw std::runtime_error("fixture send");
            sockaddr_in peer{}; int peer_size = sizeof(peer);
            const int count = recvfrom(receiver, received.data(), received.size(), 0, reinterpret_cast<sockaddr*>(&peer), &peer_size);
            if (count != size || sent != received) throw std::runtime_error("outgoing datagram boundary/payload");
            if (size) received[0] ^= 0x55;
            if (sendto(receiver, received.data(), size, 0, reinterpret_cast<const sockaddr*>(&peer), peer_size) != size)
                throw std::runtime_error("fixture reply");
            sent.fill(0);
            if (recv(sender, sent.data(), sent.size(), 0) != size || sent != received)
                throw std::runtime_error("incoming datagram boundary/payload");
        }
        DWORD short_timeout = 200;
        setsockopt(receiver, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<char*>(&short_timeout), sizeof(short_timeout));
        auto foreign = bound_socket();
        sendto(foreign, "foreign", 7, 0, reinterpret_cast<const sockaddr*>(&input), sizeof(input));
        char discarded[16];
        const int foreign_count = recv(receiver, discarded, sizeof(discarded), 0);
        const int foreign_error = WSAGetLastError();
        closesocket(foreign);
        if (foreign_count != SOCKET_ERROR || foreign_error != WSAETIMEDOUT)
            throw std::runtime_error("second source port was not rejected");
        std::array<char,5000> oversized{};
        sendto(sender, oversized.data(), oversized.size(), 0, reinterpret_cast<const sockaddr*>(&input), sizeof(input));
        if (recv(receiver, discarded, sizeof(discarded), 0) != SOCKET_ERROR || WSAGetLastError() != WSAETIMEDOUT)
            throw std::runtime_error("oversized datagram was not rejected");
        // A valid packet must still arrive after discarded traffic.
        sendto(sender, "after", 5, 0, reinterpret_cast<const sockaddr*>(&input), sizeof(input));
        if (recv(receiver, discarded, sizeof(discarded), 0) != 5 || std::string(discarded,5) != "after")
            throw std::runtime_error("datagram stream did not recover");
        // Reject a malformed pipe length without allocating/reading its body.
        char invalid_header[]{1,16}; // 4097 bytes
        if (!pipe_exact(server, invalid_header, 2, true, stop)) throw std::runtime_error("invalid header fixture write");
        const auto deadline = GetTickCount64()+2000;
        while (!stop.load() && GetTickCount64()<deadline) Sleep(10);
        if (!stop.load()) throw std::runtime_error("invalid frame did not end pump");
        stop = true;
        a.join(); b.join();
        if (ap != 5 || as != 4 || bp != 4 || bs != 5) throw std::runtime_error("datagram counts");
        std::atomic<bool> reading_done{false};
        char fragment_a[]{'a'}, fragment_b[]{'b','c','d'}, assembled[4]{};
        if (!pipe_exact(server, fragment_a, 1, true, reading_done)
            || !pipe_exact(server, fragment_b, 3, true, reading_done)
            || !pipe_exact(client, assembled, 4, false, reading_done)
            || std::string(assembled,4)!="abcd") throw std::runtime_error("partial pipe reads");
        std::cout << "Datagram roundtrips, source/size guards, malformed frame, partial reads and bounded shutdown passed." << std::endl;
    } catch (const std::exception& error) { std::cerr << error.what() << std::endl; result = 1; }
    stop = true;
    if (a.joinable()) a.join(); if (b.joinable()) b.join();
    for (auto s : {inside,outside,sender,receiver}) if (s != INVALID_SOCKET) closesocket(s);
    if (client != INVALID_HANDLE_VALUE) CloseHandle(client);
    if (server != INVALID_HANDLE_VALUE) CloseHandle(server);
    WSACleanup(); return result;
}
