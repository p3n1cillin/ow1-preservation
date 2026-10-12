#include "relay.h"
#include <algorithm>

namespace preservation {
using namespace legacy;
void Relay::broadcast(RelayResult& result, const json& message, const std::string& except) const {
    const auto bytes = encode(message);
    for (const auto& [id, player] : players_)
        if (id != except && player.joined) result.deliveries.push_back({id, bytes});
}
RelayResult Relay::open(const std::string& id) {
    if (!text(json(id), 128) || players_.contains(id)) return {false, "invalid_connection_id", {}};
    if (players_.size() >= capacity_) return {false, "room_full", {}};
    players_.emplace(id, Player{});
    return {true, {}, {{id, encode(event(Type::AssignPlayerID, id))}}};
}
RelayResult Relay::close(const std::string& id) {
    const auto it = players_.find(id);
    if (it == players_.end()) return {false, "unknown_connection", {}};
    const bool joined = it->second.joined;
    players_.erase(it);
    RelayResult result{true, {}, {}};
    if (joined) broadcast(result, event(Type::LeaveInstance, id), id);
    return result;
}
RelayResult Relay::receive(const std::string& id, std::string_view bytes, bool binary) {
    auto it = players_.find(id);
    if (it == players_.end()) return {false, "unknown_connection", {}};
    if (!binary) return {false, "binary_required", {}};
    auto message = decode(bytes);
    if (message.is_null()) return {false, "invalid_message", {}};
    auto& player = it->second;
    const auto now = std::chrono::steady_clock::now();
    player.tokens = std::min(480.0, player.tokens + std::chrono::duration<double>(now - player.refill).count() * 240);
    player.refill = now;
    if (player.tokens < 1) return {false, "rate_limit", {}};
    player.tokens -= 1;
    const auto type = static_cast<Type>(message.at("type").get<int>());
    if (type == Type::AssignPlayerID) return {false, "server_only_message", {}};
    // A socket owns exactly one player; caller-provided player IDs have no authority.
    message["player_id"] = id;
    RelayResult result{true, {}, {}};
    if (type == Type::LeaveInstance) return close(id);
    if (type == Type::JoinInstance) {
        if (player.joined) return {false, "already_joined", {}};
        for (const auto& [other_id, other] : players_) {
            if (other_id == id || !other.joined) continue;
            result.deliveries.push_back({id, encode(other.join)});
            if (!other.hero.is_null()) result.deliveries.push_back({id, encode(other.hero)});
            if (!other.position.is_null()) result.deliveries.push_back({id, encode(other.position)});
        }
        player.join = message;
        player.joined = true;
    } else {
        if (!player.joined) return {false, "join_required", {}};
        if (type == Type::ChangeHero) {
            player.hero = message; // Replace on every selection, not emplace once.
            player.position = nullptr;
        } else if (type == Type::PositionUpdate) {
            if (player.hero.is_null()) return {false, "hero_required", {}};
            if (message.at("data").at("1A0").get<int>() == -1)
                return {false, "uninitialized_movement", {}};
            player.position = message;
        }
    }
    broadcast(result, message, id);
    return result;
}
} // namespace preservation
