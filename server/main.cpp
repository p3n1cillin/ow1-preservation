#include "relay.h"
#include <ixwebsocket/IXConnectionState.h>
#include <ixwebsocket/IXNetSystem.h>
#include <ixwebsocket/IXWebSocketServer.h>
#include <charconv>
#include <iostream>
#include <mutex>

int main(int argc, char** argv) {
    std::string bind = "127.0.0.1";
    int port = 6969;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--help") {
            std::cout << "ow1-relay [--bind ADDRESS] [--port 1..65535]\n"
                         "Unauthenticated Prometheus beta movement relay; one room, 12 slots.\n";
            return 0;
        }
        if ((arg != "--bind" && arg != "--port") || i + 1 == argc) {
            std::cerr << "Invalid argument: " << arg << '\n'; return 2;
        }
        if (arg == "--bind") bind = argv[++i];
        else {
            const std::string value = argv[++i];
            const auto r = std::from_chars(value.data(), value.data() + value.size(), port);
            if (r.ec != std::errc{} || r.ptr != value.data() + value.size() || port < 1 || port > 65535) {
                std::cerr << "Invalid port\n"; return 2;
            }
        }
    }
    ix::initNetSystem();
    {
        preservation::Relay relay;
        std::mutex mutex;
        ix::WebSocketServer server(port, bind);
        std::map<std::string, ix::WebSocket*> sockets;
        server.setOnClientMessageCallback([&](std::shared_ptr<ix::ConnectionState> state,
                                              ix::WebSocket& socket, const ix::WebSocketMessagePtr& msg) {
            std::lock_guard lock(mutex);
            const auto id = state->getId();
            preservation::RelayResult result;
            if (msg->type == ix::WebSocketMessageType::Open) {
                sockets[id] = &socket;
                result = relay.open(id);
            } else if (msg->type == ix::WebSocketMessageType::Message) {
                result = relay.receive(id, msg->str, msg->binary);
            } else if (msg->type == ix::WebSocketMessageType::Close || msg->type == ix::WebSocketMessageType::Error) {
                if (!relay.contains(id)) { sockets.erase(id); return; }
                result = relay.close(id);
                sockets.erase(id);
            } else return;
            if (!result.accepted) {
                std::cout << preservation::legacy::json{{"event", "rejected"}, {"connection", id}, {"reason", result.error}}.dump() << std::endl;
                socket.close(1008, result.error);
            } else if (msg->type == ix::WebSocketMessageType::Message && !relay.contains(id)) {
                socket.close(1000, "left_room");
            }
            for (const auto& delivery : result.deliveries) {
                const auto target = sockets.find(delivery.recipient);
                if (target == sockets.end()) continue;
                if (target->second->bufferedAmount() > 1024 * 1024)
                    target->second->close(1008, "slow_consumer");
                else target->second->sendBinary(delivery.bytes);
            }
            if (msg->type != ix::WebSocketMessageType::Message)
                std::cout << preservation::legacy::json{{"event", "connections"}, {"count", relay.size()}}.dump() << std::endl;
        });
        const auto listening = server.listen();
        if (!listening.first) { std::cerr << listening.second << '\n'; return 1; }
        server.start();
        std::cout << preservation::legacy::json{{"event", "listening"}, {"bind", bind}, {"port", port}, {"protocol", "prometheus-demo-v0"}}.dump() << std::endl;
        server.wait();
    }
    ix::uninitNetSystem();
}
