#pragma once
// Container-loopback bridge for private-service experiments.
//
// An AppContainer process with no network capabilities can still reach a
// loopback listener owned by the *same* AppContainer, but not one owned by a
// normal desktop process. The bridge therefore runs in two halves:
//   * inside the client's AppContainer it listens on 127.0.0.1:<port>;
//   * each accepted connection opens a named pipe whose DACL names only the
//     owner and that AppContainer SID (with a low-integrity label);
//   * the host launcher forwards each pipe instance to 127.0.0.1:<host port>.
// The client never receives a network capability, so Internet and LAN access
// stay denied; only explicitly configured host loopback ports are reachable.
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <sddl.h>
#include <atomic>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace loopback_bridge {

struct Forward { uint16_t container_port = 0, host_port = 0; };

inline std::mutex log_mutex;
template<typename... T> void log(const T&... parts) {
    std::lock_guard lock(log_mutex);
    ((std::cout << parts), ...);
    std::cout << std::endl;
}

inline Forward parse_forward(const std::wstring& text) {
    const auto colon = text.find(L':');
    auto port = [](const std::wstring& value) {
        if (value.empty() || value.size() > 5 || value.find_first_not_of(L"0123456789") != std::wstring::npos)
            throw std::runtime_error("Forward ports must be decimal");
        const auto number = std::stoul(value);
        if (number == 0 || number > 65535) throw std::runtime_error("Forward port out of range");
        return static_cast<uint16_t>(number);
    };
    Forward forward;
    forward.container_port = port(text.substr(0, colon));
    forward.host_port = colon == std::wstring::npos ? forward.container_port : port(text.substr(colon + 1));
    return forward;
}

inline std::wstring pipe_name(DWORD owner_pid, uint16_t container_port) {
    return L"\\\\.\\pipe\\ow1-bridge-" + std::to_wstring(owner_pid) + L"-" + std::to_wstring(container_port);
}

// Copies bytes in both directions until either side ends. The pipe handle is
// overlapped so the two directions do not serialize on one handle.
inline void pump(HANDLE pipe, SOCKET socket_handle, uint64_t& to_pipe, uint64_t& to_socket) {
    std::atomic<bool> done{false};
    auto finish = [&]() {
        if (!done.exchange(true)) {
            shutdown(socket_handle, SD_BOTH);
            CancelIoEx(pipe, nullptr);
        }
    };
    std::thread upstream([&]() {
        std::vector<char> buffer(64 * 1024);
        OVERLAPPED overlapped{}; overlapped.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        for (;;) {
            const int received = recv(socket_handle, buffer.data(), static_cast<int>(buffer.size()), 0);
            if (received <= 0) break;
            DWORD written = 0; ResetEvent(overlapped.hEvent);
            if (!WriteFile(pipe, buffer.data(), received, nullptr, &overlapped) && GetLastError() != ERROR_IO_PENDING) break;
            if (!GetOverlappedResult(pipe, &overlapped, &written, TRUE) || written != static_cast<DWORD>(received)) break;
            to_pipe += written;
        }
        CloseHandle(overlapped.hEvent);
        finish();
    });
    {
        std::vector<char> buffer(64 * 1024);
        OVERLAPPED overlapped{}; overlapped.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
        for (;;) {
            DWORD read = 0; ResetEvent(overlapped.hEvent);
            if (!ReadFile(pipe, buffer.data(), static_cast<DWORD>(buffer.size()), nullptr, &overlapped)
                && GetLastError() != ERROR_IO_PENDING) break;
            if (!GetOverlappedResult(pipe, &overlapped, &read, TRUE) || read == 0) break;
            int offset = 0;
            while (offset < static_cast<int>(read)) {
                const int sent = send(socket_handle, buffer.data() + offset, static_cast<int>(read) - offset, 0);
                if (sent <= 0) { offset = -1; break; }
                offset += sent;
            }
            if (offset < 0) break;
            to_socket += read;
        }
        CloseHandle(overlapped.hEvent);
        finish();
    }
    upstream.join();
}

inline SOCKET loopback_socket() {
    SOCKET handle = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (handle == INVALID_SOCKET) throw std::runtime_error("Bridge socket: " + std::to_string(WSAGetLastError()));
    return handle;
}

inline sockaddr_in loopback_address(uint16_t port) {
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    return address;
}

// ---- Container half -------------------------------------------------------

inline void container_connection(SOCKET client, std::wstring name, uint16_t port) {
    HANDLE pipe = INVALID_HANDLE_VALUE;
    for (int attempt = 0; attempt < 50 && pipe == INVALID_HANDLE_VALUE; ++attempt) {
        pipe = CreateFileW(name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, nullptr);
        if (pipe == INVALID_HANDLE_VALUE) {
            const auto error = GetLastError();
            if (error != ERROR_PIPE_BUSY && error != ERROR_FILE_NOT_FOUND) {
                log("bridge: pipe open for port ", port, " failed Win32=", error);
                break;
            }
            WaitNamedPipeW(name.c_str(), 100);
        }
    }
    if (pipe == INVALID_HANDLE_VALUE) { closesocket(client); return; }
    uint64_t up = 0, down = 0;
    pump(pipe, client, up, down);
    CloseHandle(pipe);
    closesocket(client);
}

// Entry point for `--loopback-bridge OWNER_PID PORT...` inside the AppContainer.
inline int run_container(int argc, wchar_t** argv) {
    WSADATA wsa{};
    if (WSAStartup(MAKEWORD(2, 2), &wsa)) return 3;
    const DWORD owner = std::stoul(argv[2]);
    std::vector<std::thread> listeners;
    for (int n = 3; n < argc; ++n) {
        const auto port = parse_forward(argv[n]).container_port;
        SOCKET listener = loopback_socket();
        const auto address = loopback_address(port);
        if (bind(listener, reinterpret_cast<const sockaddr*>(&address), sizeof(address)) || listen(listener, SOMAXCONN)) {
            log("bridge: container listen 127.0.0.1:", port, " failed WSA=", WSAGetLastError());
            return 4;
        }
        listeners.emplace_back([listener, owner, port]() {
            const auto name = pipe_name(owner, port);
            for (;;) {
                SOCKET client = accept(listener, nullptr, nullptr);
                if (client == INVALID_SOCKET) return;
                std::thread(container_connection, client, name, port).detach();
            }
        });
    }
    for (auto& listener : listeners) listener.join();
    return 0;
}

// ---- Host half ------------------------------------------------------------

class HostForwarder {
public:
    HostForwarder(PSID container, std::vector<Forward> forwards) : forwards_(std::move(forwards)) {
        WSADATA wsa{};
        if (WSAStartup(MAKEWORD(2, 2), &wsa)) throw std::runtime_error("Host bridge Winsock startup");
        LPWSTR owner = nullptr, sandbox = nullptr;
        HANDLE token = nullptr;
        if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token)) throw std::runtime_error("Host bridge token");
        std::vector<unsigned char> user(256); DWORD size = 0;
        const bool have_user = GetTokenInformation(token, TokenUser, user.data(), static_cast<DWORD>(user.size()), &size);
        CloseHandle(token);
        if (!have_user || !ConvertSidToStringSidW(reinterpret_cast<TOKEN_USER*>(user.data())->User.Sid, &owner)
            || !ConvertSidToStringSidW(container, &sandbox))
            throw std::runtime_error("Host bridge SID conversion");
        // Owner and this one AppContainer only; low label so the Low-IL
        // container token may write to the pipe.
        sddl_ = std::wstring(L"D:P(A;;GA;;;") + owner + L")(A;;GRGW;;;" + sandbox + L")S:(ML;;NW;;;LW)";
        LocalFree(owner); LocalFree(sandbox);
    }

    void start() {
        for (const auto forward : forwards_) {
            std::thread(&HostForwarder::serve, this, forward).detach();
            log("bridge: container 127.0.0.1:", forward.container_port, " -> host 127.0.0.1:", forward.host_port);
        }
    }

private:
    void serve(Forward forward) {
        const auto name = pipe_name(GetCurrentProcessId(), forward.container_port);
        unsigned connection = 0;
        for (;;) {
            PSECURITY_DESCRIPTOR descriptor = nullptr;
            if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl_.c_str(), SDDL_REVISION_1, &descriptor, nullptr)) {
                log("bridge: pipe descriptor failed Win32=", GetLastError());
                return;
            }
            SECURITY_ATTRIBUTES attributes{sizeof(attributes), descriptor, FALSE};
            HANDLE pipe = CreateNamedPipeW(name.c_str(), PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED,
                PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
                PIPE_UNLIMITED_INSTANCES, 64 * 1024, 64 * 1024, 0, &attributes);
            LocalFree(descriptor);
            if (pipe == INVALID_HANDLE_VALUE) { log("bridge: create pipe failed Win32=", GetLastError()); return; }
            OVERLAPPED overlapped{}; overlapped.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
            DWORD ignored = 0;
            const bool connected = ConnectNamedPipe(pipe, &overlapped)
                || GetLastError() == ERROR_PIPE_CONNECTED
                || (GetLastError() == ERROR_IO_PENDING && GetOverlappedResult(pipe, &overlapped, &ignored, TRUE));
            CloseHandle(overlapped.hEvent);
            if (!connected) { CloseHandle(pipe); continue; }
            const unsigned id = ++connection;
            std::thread([pipe, forward, id]() {
                SOCKET upstream = loopback_socket();
                const auto address = loopback_address(forward.host_port);
                if (connect(upstream, reinterpret_cast<const sockaddr*>(&address), sizeof(address))) {
                    log("bridge: port ", forward.container_port, " #", id, " host 127.0.0.1:", forward.host_port,
                        " refused WSA=", WSAGetLastError());
                    closesocket(upstream); DisconnectNamedPipe(pipe); CloseHandle(pipe);
                    return;
                }
                log("bridge: port ", forward.container_port, " #", id, " opened");
                uint64_t to_host = 0, to_container = 0;
                // Host side: the pipe carries container->host bytes.
                pump(pipe, upstream, to_container, to_host);
                log("bridge: port ", forward.container_port, " #", id, " closed; client->host ", to_host,
                    " bytes, host->client ", to_container, " bytes");
                closesocket(upstream); DisconnectNamedPipe(pipe); CloseHandle(pipe);
            }).detach();
        }
    }

    std::vector<Forward> forwards_;
    std::wstring sddl_;
};

} // namespace loopback_bridge
