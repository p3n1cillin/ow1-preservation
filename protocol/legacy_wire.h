#pragma once
#include <nlohmann/json.hpp>
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>
#include <string_view>
#include <vector>

// Prometheus demo protocol v0, NOT the original game's JAM protocol.
// Numeric message IDs and BSON field names must remain wire compatible.
namespace preservation::legacy {
using json = nlohmann::json;
enum class Type { None = 0, ChangeHero = 1, PositionUpdate = 2,
                  JoinInstance = 3, LeaveInstance = 4, AssignPlayerID = 5 };
inline constexpr std::size_t max_message_bytes = 16384;

inline bool integer(const json& value, std::int64_t low, std::int64_t high) {
    if (!value.is_number_integer()) return false;
    if (value.is_number_unsigned()) {
        const auto n = value.get<std::uint64_t>();
        return n <= static_cast<std::uint64_t>(high) && (low <= 0 || n >= static_cast<std::uint64_t>(low));
    }
    const auto n = value.get<std::int64_t>();
    return n >= low && n <= high;
}
inline bool scalar(const json& value) {
    if (!value.is_number()) return false;
    const auto n = value.get<double>();
    return std::isfinite(n) && std::abs(n) <= (std::numeric_limits<float>::max)();
}
inline bool text(const json& value, std::size_t limit) {
    return value.is_string() && !value.get_ref<const std::string&>().empty()
        && value.get_ref<const std::string&>().size() <= limit
        && value.get_ref<const std::string&>().find('\0') == std::string::npos;
}
inline bool movement(const json& data) {
    if (!data.is_object()) return false;
    // Exactly the fields read by prometheus/serialization.cpp. Lists, pointers
    // and the rotation matrix are intentionally absent in the upstream codec.
    for (auto key : {"0", "10", "50", "70", "90", "200", "220", "230", "250"}) {
        const auto& v = data.at(key);
        if (!v.is_object()) return false;
        for (auto axis : {"x", "y", "z", "w"}) if (!scalar(v.at(axis))) return false;
    }
    for (auto key : {"20", "38", "B8", "C0", "C4", "C8", "D0", "1AC", "1B8",
                     "1BC", "210", "214", "218", "240"})
        if (!scalar(data.at(key))) return false;
    for (auto key : {"30", "34", "40", "80", "84", "88", "BC", "CC", "198", "19C",
                     "1A0", "1A4", "1A8", "1B4", "248"})
        if (!integer(data.at(key), INT32_MIN, INT32_MAX)) return false;
    if (!integer(data.at("60"), INT16_MIN, INT16_MAX) ||
        !integer(data.at("244"), 0, UINT32_MAX)) return false;
    for (auto key : {"8C", "B0", "21C", "21D", "268"})
        if (!integer(data.at(key), INT8_MIN, INT8_MAX)) return false;
    for (auto key : {"1B0", "1B2"}) {
        const auto& v = data.at(key);
        if (!v.is_object() || !integer(v.at("lr"), 0, UINT8_MAX) ||
            !integer(v.at("fb"), 0, UINT8_MAX)) return false;
    }
    return true;
}
inline bool valid(const json& message) noexcept {
    try {
        if (!message.is_object() || !integer(message.at("type"), 1, 5) ||
            !text(message.at("player_id"), 128)) return false;
        switch (static_cast<Type>(message.at("type").get<int>())) {
        case Type::ChangeHero:
            return integer(message.at("heroid"), 1, INT64_MAX) &&
                   integer(message.at("skinid"), 0, INT64_MAX);
        case Type::PositionUpdate: return movement(message.at("data"));
        case Type::JoinInstance: return text(message.at("name"), 64);
        case Type::LeaveInstance: case Type::AssignPlayerID: return true;
        default: return false;
        }
    } catch (const json::exception&) { return false; }
}
inline json decode(std::string_view bytes) noexcept {
    if (bytes.size() > max_message_bytes || bytes.size() < 5) return nullptr;
    try {
        auto message = json::from_bson(bytes.begin(), bytes.end());
        return valid(message) ? message : json(nullptr);
    } catch (const json::exception&) { return nullptr; }
}
inline std::string encode(const json& message) {
    const auto bytes = json::to_bson(message);
    return {bytes.begin(), bytes.end()};
}
inline json event(Type type, const std::string& id) {
    return {{"type", static_cast<int>(type)}, {"player_id", id}};
}
} // namespace preservation::legacy
