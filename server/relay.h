#pragma once
#include "../protocol/legacy_wire.h"
#include <chrono>
#include <map>
#include <optional>

namespace preservation {
struct Delivery { std::string recipient; std::string bytes; };
struct RelayResult {
    bool accepted = false;
    std::string error;
    std::vector<Delivery> deliveries;
};

// Transport-independent single-room compatibility adapter. No combat or
// authority over movement is implied. The transport serializes access.
class Relay {
    struct Player {
        bool joined = false;
        legacy::json join, hero, position;
        double tokens = 480;
        std::chrono::steady_clock::time_point refill = std::chrono::steady_clock::now();
    };
    std::map<std::string, Player> players_;
    std::size_t capacity_;
    void broadcast(RelayResult& result, const legacy::json& message, const std::string& except) const;
public:
    explicit Relay(std::size_t capacity = 12) : capacity_(capacity) {}
    RelayResult open(const std::string& id);
    RelayResult receive(const std::string& id, std::string_view bytes, bool binary = true);
    RelayResult close(const std::string& id);
    std::size_t size() const { return players_.size(); }
    bool contains(const std::string& id) const { return players_.contains(id); }
};
} // namespace preservation
