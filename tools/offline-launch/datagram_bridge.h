#pragma once
// Diagnostic datagram transport over the existing owner/AppContainer pipe.
// One container-loopback peer per port; fixed host loopback destination only.
// Frames are a little-endian uint16 length followed by one datagram (<=4096).
// This carries packets without changing native transport or network capability.
namespace loopback_bridge {
inline bool pipe_exact(HANDLE pipe, char* bytes, DWORD size, bool writing, const std::atomic<bool>& done) {
    OVERLAPPED operation{}; operation.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    if (!operation.hEvent) return false;
    DWORD offset = 0;
    while (offset < size && !done.load()) {
        ResetEvent(operation.hEvent);
        DWORD count = 0;
        const bool started = writing
            ? WriteFile(pipe, bytes + offset, size - offset, nullptr, &operation) != FALSE
            : ReadFile(pipe, bytes + offset, size - offset, nullptr, &operation) != FALSE;
        const DWORD error = started ? ERROR_SUCCESS : GetLastError();
        if (!started && error == ERROR_IO_PENDING) {
            while (WaitForSingleObject(operation.hEvent, 250) == WAIT_TIMEOUT) {
                if (done.load()) { CancelIoEx(pipe, &operation); break; }
            }
        }
        if ((!started && error != ERROR_IO_PENDING)
            || !GetOverlappedResult(pipe, &operation, &count, TRUE) || !count) break;
        offset += count;
    }
    CloseHandle(operation.hEvent);
    return offset == size;
}

inline SOCKET datagram_socket() {
    const SOCKET handle = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (handle == INVALID_SOCKET) throw std::runtime_error("Datagram bridge socket");
    return handle;
}

inline void pump_datagrams(HANDLE pipe, SOCKET socket_handle, bool container,
                          uint64_t& to_pipe, uint64_t& to_socket, std::atomic<bool>* stop = nullptr) {
    std::atomic<bool> local_done{false};
    auto& done = stop ? *stop : local_done;
    std::mutex peer_mutex;
    sockaddr_in peer{};
    const auto finish = [&]() {
        if (!done.exchange(true)) {
            shutdown(socket_handle, SD_BOTH);
            CancelIoEx(pipe, nullptr);
        }
    };
    std::thread upstream([&]() {
        char buffer[4098];
        while (!done.load()) {
            fd_set readable; FD_ZERO(&readable); FD_SET(socket_handle, &readable);
            timeval timeout{0, 250000};
            const int ready = select(0, &readable, nullptr, nullptr, &timeout);
            if (!ready) continue;
            if (ready < 0) break;
            sockaddr_in sender{}; int sender_size = sizeof(sender);
            const int count = container
                ? recvfrom(socket_handle, buffer + 2, 4096, 0, reinterpret_cast<sockaddr*>(&sender), &sender_size)
                : recv(socket_handle, buffer + 2, 4096, 0);
            if (count < 0) {
                if (WSAGetLastError() == WSAEMSGSIZE) continue;
                break;
            }
            if (container) {
                if (sender.sin_family != AF_INET || sender.sin_addr.s_addr != htonl(INADDR_LOOPBACK)) continue;
                std::lock_guard lock(peer_mutex);
                if (peer.sin_port && peer.sin_port != sender.sin_port) continue;
                peer = sender;
            }
            buffer[0] = static_cast<char>(count & 255);
            buffer[1] = static_cast<char>((count >> 8) & 255);
            if (!pipe_exact(pipe, buffer, count + 2, true, done)) break;
            ++to_pipe;
        }
        finish();
    });
    char buffer[4096], header[2];
    while (!done.load()) {
        if (!pipe_exact(pipe, header, 2, false, done)) break;
        const unsigned size = static_cast<unsigned char>(header[0])
            | (static_cast<unsigned>(static_cast<unsigned char>(header[1])) << 8);
        if (size > sizeof(buffer) || (size && !pipe_exact(pipe, buffer, size, false, done))) break;
        int count;
        if (container) {
            std::lock_guard lock(peer_mutex);
            if (!peer.sin_port) break;
            count = sendto(socket_handle, buffer, size, 0, reinterpret_cast<const sockaddr*>(&peer), sizeof(peer));
        } else count = send(socket_handle, buffer, size, 0);
        if (count != static_cast<int>(size)) break;
        ++to_socket;
    }
    finish();
    upstream.join();
}
} // namespace loopback_bridge
