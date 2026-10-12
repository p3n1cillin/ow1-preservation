#ifdef _WIN32
#define NOMINMAX
#include <winsock2.h>
#include <windows.h>
#else
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/wait.h>
#include <signal.h>
#endif
#include "fixtures.h"
#include <ixwebsocket/IXNetSystem.h>
#include <ixwebsocket/IXWebSocket.h>
#include <condition_variable>
#include <filesystem>
#include <mutex>
#include <thread>
#include <memory>

using namespace preservation::legacy;
using namespace std::chrono_literals;
int free_port() {
    const auto socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr{}; addr.sin_family = AF_INET; addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    check(bind(socket_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0, "reserve test port");
#ifdef _WIN32
    int len = sizeof(addr);
#else
    socklen_t len = sizeof(addr);
#endif
    check(getsockname(socket_fd, reinterpret_cast<sockaddr*>(&addr), &len) == 0, "read test port");
#ifdef _WIN32
    closesocket(socket_fd);
#else
    close(socket_fd);
#endif
    return ntohs(addr.sin_port);
}
struct Child {
#ifdef _WIN32
    HANDLE process = nullptr;
    Child(const char* path, int port) {
        const auto exe = std::filesystem::path(path).wstring();
        auto command = L"\"" + exe + L"\" --port " + std::to_wstring(port);
        STARTUPINFOW startup{}; startup.cb = sizeof(startup); PROCESS_INFORMATION info{};
        check(CreateProcessW(exe.c_str(), command.data(), nullptr, nullptr, FALSE, CREATE_NO_WINDOW,
                             nullptr, nullptr, &startup, &info) != FALSE, "start dedicated server");
        process = info.hProcess; CloseHandle(info.hThread);
    }
    ~Child() { if (process) { TerminateProcess(process, 0); WaitForSingleObject(process, 2000); CloseHandle(process); } }
#else
    pid_t process;
    Child(const char* path, int port) {
        const auto value = std::to_string(port); process = fork();
        check(process >= 0, "fork server");
        if (process == 0) { execl(path, path, "--port", value.c_str(), nullptr); _exit(127); }
    }
    ~Child() { kill(process, SIGTERM); waitpid(process, nullptr, 0); }
#endif
};
struct Client {
    ix::WebSocket socket;
    std::mutex mutex; std::condition_variable changed;
    std::vector<json> messages;
    bool closed = false;
    explicit Client(int port) {
        socket.setUrl("ws://127.0.0.1:" + std::to_string(port) + "/");
        socket.disableAutomaticReconnection();
        socket.setOnMessageCallback([this](const ix::WebSocketMessagePtr& msg) {
            std::lock_guard lock(mutex);
            if (msg->type == ix::WebSocketMessageType::Message) {
                auto value = decode(msg->str); if (!value.is_null()) messages.push_back(std::move(value));
            }
            if (msg->type == ix::WebSocketMessageType::Close) closed = true;
            changed.notify_all();
        });
        socket.start();
    }
    ~Client() { socket.stop(); }
    json wait(Type type, const std::string& id = "") {
        std::unique_lock lock(mutex);
        auto match = [&]() { return std::find_if(messages.begin(), messages.end(), [&](const json& j) {
            return j.at("type") == static_cast<int>(type) && (id.empty() || j.at("player_id") == id);
        }); };
        check(changed.wait_for(lock, 5s, [&] { return match() != messages.end(); }), "timed out waiting for protocol event");
        auto it = match(); auto result = *it; messages.erase(it); return result;
    }
    void wait_closed() {
        std::unique_lock lock(mutex);
        check(changed.wait_for(lock, 5s, [&] { return closed; }), "rejected client was not closed");
    }
    void send(const json& j) { check(socket.sendBinary(encode(j)).success, "send BSON"); }
};
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    ix::initNetSystem();
    try {
        const int port = free_port(); Child child(argv[1], port);
        // Readiness: retry connection with a bounded deadline, no fixed startup delay.
        bool ready = false;
        const auto deadline = std::chrono::steady_clock::now() + 5s;
        while (std::chrono::steady_clock::now() < deadline) {
            ix::WebSocket probe; probe.setUrl("ws://127.0.0.1:" + std::to_string(port));
            probe.setOnMessageCallback([](const ix::WebSocketMessagePtr&) {});
            if (probe.connect(1).success) { ready = true; break; }
            std::this_thread::sleep_for(25ms);
        }
        check(ready, "server readiness");
        // The probe may remain visible until server close callback; allow its close handshake.
        std::this_thread::sleep_for(100ms);
        Client a(port); const auto a_id = a.wait(Type::AssignPlayerID).at("player_id").get<std::string>();
        a.send(join_fixture(a_id)); a.send(hero_fixture(a_id)); a.send(position_fixture(a_id,10,17.5));
        Client b(port); const auto b_id = b.wait(Type::AssignPlayerID).at("player_id").get<std::string>();
        b.send(join_fixture(b_id));
        b.wait(Type::JoinInstance,a_id); b.wait(Type::ChangeHero,a_id);
        check(b.wait(Type::PositionUpdate,a_id).at("data").at("220").at("x") == 17.5, "late join movement on actual sockets");
        b.send(hero_fixture("impersonated",2));
        check(a.wait(Type::ChangeHero,b_id).at("heroid") == 2, "socket identity ownership");
        b.send(position_fixture(a_id,11,-4.25));
        check(a.wait(Type::PositionUpdate,b_id).at("data").at("220").at("x") == -4.25, "two participant movement");
        a.send(hero_fixture(a_id,3));
        check(b.wait(Type::ChangeHero,a_id).at("heroid") == 3, "hero reselection");
        b.socket.stop(); a.wait(Type::LeaveInstance,b_id);
        Client rejoined(port); const auto new_id = rejoined.wait(Type::AssignPlayerID).at("player_id").get<std::string>();
        check(new_id != b_id, "new session identity on reconnect"); rejoined.send(join_fixture(new_id));
        rejoined.wait(Type::JoinInstance,a_id);
        check(rejoined.wait(Type::ChangeHero,a_id).at("heroid") == 3, "reconnect gets latest selection");
        rejoined.socket.stop(); a.wait(Type::LeaveInstance,new_id);
        {
            Client leaving(port);
            const auto leaving_id = leaving.wait(Type::AssignPlayerID).at("player_id").get<std::string>();
            leaving.send(join_fixture(leaving_id)); a.wait(Type::JoinInstance,leaving_id);
            leaving.send(event(Type::LeaveInstance,a_id));
            leaving.wait_closed(); a.wait(Type::LeaveInstance,leaving_id);
        }
        std::vector<std::unique_ptr<Client>> peers;
        for (int i=0;i<11;++i) {
            auto peer = std::make_unique<Client>(port); const auto id = peer->wait(Type::AssignPlayerID).at("player_id").get<std::string>();
            peer->send(join_fixture(id)); peer->send(hero_fixture(id)); peer->send(position_fixture(id,i+20,i));
            a.wait(Type::PositionUpdate,id); peers.push_back(std::move(peer));
        }
        { Client excess(port); excess.wait_closed(); }
        // One malformed sender is disconnected; the remaining sockets keep relaying.
        peers.back()->socket.sendBinary("invalid bson"); peers.back()->wait_closed(); peers.pop_back();
        a.send(position_fixture(a_id,40,23));
        check(peers.front()->wait(Type::PositionUpdate,a_id).at("data").at("220").at("x") == 23, "server survives malformed peer");
        peers.clear();
        a.socket.stop();
        std::cout << "PASS: dedicated process, two-way movement, late join, hero change, reconnect, 12 sockets, capacity, malformed peer\n";
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; ix::uninitNetSystem(); return 1; }
    ix::uninitNetSystem(); return 0;
}
