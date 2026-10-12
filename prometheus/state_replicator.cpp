#include "state_replicator.h"
#include <ixwebsocket/IXNetSystem.h>
#include "serialization.h"

void state_replicator::network_init() {
    std::call_once(_network_init, [] { ix::initNetSystem(); });
}
state_replicator::playerid state_replicator::get_local_playerid() {
    std::lock_guard lock(_local_state_mut);
    return _local_playerid;
}
void state_replicator::ws_client_callback(const ix::WebSocketMessagePtr& ws_msg) {
    if (ws_msg->type == ix::WebSocketMessageType::Message) {
        const auto json = ws_msg->binary ? preservation::legacy::decode(ws_msg->str) : nlohmann::json(nullptr);
        if (json.is_null()) {
            printf("state_replicator: rejected malformed or nonbinary message\n");
            return;
        }
        auto msg = deserialize_message(json);
        if (msg->type == MsgBase::MessageType::AssignPlayerID) {
            ChangeHeroMessage hero;
            {
                std::lock_guard lock(_local_state_mut);
                _local_playerid = dynamic_cast<AssignPlayerIDMessage*>(msg.get())->player_id;
                hero = _local_hero;
                hero.player_id = _local_playerid;
            }
            {
                std::lock_guard lock(_outstanding_messages_mut);
                _outstanding_messages.clear();
            }
            JoinInstanceMessage join;
            join.player_id = hero.player_id;
            join.name = "Remote Player";
            _ws.sendBinary(serialize_message(&join));
            if (hero.heroid != 0) _ws.sendBinary(serialize_message(&hero));
            is_connected = true;
            printf("state_replicator: assigned local identity %s\n", hero.player_id.c_str());
            return;
        }
        push_message(msg);
    } else if (ws_msg->type == ix::WebSocketMessageType::Close || ws_msg->type == ix::WebSocketMessageType::Error) {
        is_connected = false;
        std::lock_guard lock(_local_state_mut);
        _local_playerid.clear();
    }
}
void state_replicator::deliver(const preservation::RelayResult& result) {
    // Caller holds _relay_mut. The embedded host is a participant, not a socket.
    for (const auto& delivery : result.deliveries) {
        if (delivery.recipient == "Server") {
            push_message(deserialize_message(preservation::legacy::decode(delivery.bytes)));
        } else if (const auto it = _sockets.find(delivery.recipient); it != _sockets.end()) {
            if (it->second->bufferedAmount() > 1024 * 1024) it->second->close(1008, "slow_consumer");
            else it->second->sendBinary(delivery.bytes);
        }
    }
}
void state_replicator::ws_server_callback(std::shared_ptr<ix::ConnectionState> state, ix::WebSocket& ws,
                                         const ix::WebSocketMessagePtr& ws_msg) {
    std::lock_guard lock(_relay_mut);
    preservation::RelayResult result;
    const auto id = state->getId();
    if (ws_msg->type == ix::WebSocketMessageType::Open) {
        _sockets[id] = &ws;
        result = _relay.open(id);
    } else if (ws_msg->type == ix::WebSocketMessageType::Message) {
        result = _relay.receive(id, ws_msg->str, ws_msg->binary);
    } else if (ws_msg->type == ix::WebSocketMessageType::Close || ws_msg->type == ix::WebSocketMessageType::Error) {
        if (!_relay.contains(id)) { _sockets.erase(id); return; }
        result = _relay.close(id);
        _sockets.erase(id);
    } else return;
    if (!result.accepted) {
        printf("state_replicator: rejected connection message: %s\n", result.error.c_str());
        ws.close(1008, result.error);
    } else if (ws_msg->type == ix::WebSocketMessageType::Message && !_relay.contains(id)) {
        ws.close(1000, "left_room");
    }
    deliver(result);
}
void state_replicator::push_message(std::shared_ptr<MsgBase> msg) {
    if (!msg || msg->type == MsgBase::MessageType::None) return;
    std::unique_lock lock(_outstanding_messages_mut);
    if (_outstanding_messages.size() >= 4096) {
        _outstanding_messages.clear();
        is_connected = false;
        lock.unlock();
        _ws.close(1008, "receive_queue_full");
        printf("state_replicator: receive queue full; disconnecting\n");
        return;
    }
    _outstanding_messages.push_back(std::move(msg));
}
std::vector<std::uint8_t> state_replicator::serialize_message(MsgBase* msg) {
    nlohmann::json json;
    switch (msg->type) {
    case MsgBase::MessageType::ChangeHero: json = *dynamic_cast<ChangeHeroMessage*>(msg); break;
    case MsgBase::MessageType::JoinInstance: json = *dynamic_cast<JoinInstanceMessage*>(msg); break;
    case MsgBase::MessageType::LeaveInstance: json = *dynamic_cast<LeaveInstanceMessage*>(msg); break;
    case MsgBase::MessageType::PositionUpdate: json = *dynamic_cast<PositionUpdateMessage*>(msg); break;
    case MsgBase::MessageType::AssignPlayerID: json = *dynamic_cast<AssignPlayerIDMessage*>(msg); break;
    default: return {};
    }
    return nlohmann::json::to_bson(json);
}
std::shared_ptr<state_replicator::MsgBase> state_replicator::deserialize_message(nlohmann::json input) {
    if (!preservation::legacy::valid(input)) return std::make_shared<NoneMessage>();
    try {
        switch (input.at("type").get<MsgBase::MessageType>()) {
        case MsgBase::MessageType::ChangeHero: return std::make_shared<ChangeHeroMessage>(input.get<ChangeHeroMessage>());
        case MsgBase::MessageType::JoinInstance: return std::make_shared<JoinInstanceMessage>(input.get<JoinInstanceMessage>());
        case MsgBase::MessageType::LeaveInstance: return std::make_shared<LeaveInstanceMessage>(input.get<LeaveInstanceMessage>());
        case MsgBase::MessageType::PositionUpdate: return std::make_shared<PositionUpdateMessage>(input.get<PositionUpdateMessage>());
        case MsgBase::MessageType::AssignPlayerID: return std::make_shared<AssignPlayerIDMessage>(input.get<AssignPlayerIDMessage>());
        default: break;
        }
    } catch (const nlohmann::json::exception& ex) {
        printf("state_replicator: deserialize failed: %s\n", ex.what());
    }
    return std::make_shared<NoneMessage>();
}
void state_replicator::disconnect() {
    is_connected = false;
    _ws.stop();
    if (_is_server.exchange(false)) _wss.stop();
    {
        std::lock_guard lock(_relay_mut);
        _sockets.clear();
        _relay = preservation::Relay{};
    }
    {
        std::lock_guard lock(_local_state_mut);
        _local_playerid.clear();
    }
    std::lock_guard lock(_outstanding_messages_mut);
    _outstanding_messages.clear();
}
void state_replicator::start_server() {
    network_init();
    disconnect();
    _wss.setOnClientMessageCallback(ws_server_callback);
    const auto result = _wss.listen();
    if (!result.first) { printf("Failed to start server: %s\n", result.second.c_str()); return; }
    ChangeHeroMessage hero;
    {
        std::lock_guard lock(_local_state_mut);
        _local_playerid = "Server";
        hero = _local_hero;
    }
    {
        std::lock_guard lock(_relay_mut);
        _relay.open("Server");
        auto join = preservation::legacy::event(preservation::legacy::Type::JoinInstance, "Server");
        join["name"] = "Local host";
        _relay.receive("Server", preservation::legacy::encode(join));
    }
    _is_server = true;
    is_connected = true;
    _wss.start();
    if (hero.heroid != 0) emplace_hero_update(hero);
    printf("state_replicator: embedded relay listening on 127.0.0.1:6969\n");
}
void state_replicator::connect(std::string ip_addr, unsigned short port) {
    network_init();
    disconnect();
    _ws.setUrl("ws://" + ip_addr + ":" + std::to_string(port) + "/");
    _ws.setPingInterval(1);
    _ws.setOnMessageCallback(ws_client_callback);
    _ws.disableAutomaticReconnection();
    _ws.start(); // connect() alone never pumps received messages.
}
std::shared_ptr<state_replicator::MsgBase> state_replicator::get_outstanding_message() {
    std::lock_guard lock(_outstanding_messages_mut);
    if (_outstanding_messages.empty()) return std::make_shared<NoneMessage>();
    auto msg = _outstanding_messages.front();
    _outstanding_messages.erase(_outstanding_messages.begin());
    return msg;
}
void state_replicator::send_local(const std::vector<std::uint8_t>& bytes) {
    if (_is_server) {
        std::lock_guard lock(_relay_mut);
        const std::string_view data(reinterpret_cast<const char*>(bytes.data()), bytes.size());
        auto result = _relay.receive("Server", data);
        if (result.accepted) deliver(result);
    } else if (is_connected) _ws.sendBinary(bytes);
}
void state_replicator::emplace_positon_update(MovementState* state) {
    if (!state || state->command_frame == -1 || !is_connected) return;
    PositionUpdateMessage msg;
    {
        std::lock_guard lock(_local_state_mut);
        if (_local_hero.heroid == 0) return;
        msg.player_id = _local_playerid;
    }
    if (msg.player_id.empty()) return;
    msg.data = *state;
    send_local(serialize_message(&msg));
}
void state_replicator::emplace_hero_update(ChangeHeroMessage msg) {
    {
        std::lock_guard lock(_local_state_mut);
        msg.player_id = _local_playerid;
        _local_hero = msg;
    }
    if (is_connected && !msg.player_id.empty()) send_local(serialize_message(&msg));
}
