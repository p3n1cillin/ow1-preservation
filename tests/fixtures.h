#pragma once
#include "protocol/legacy_wire.h"
#include <stdexcept>
#include <iostream>

inline void check(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
inline preservation::legacy::json movement_fixture(int frame = 1, double x = 0) {
    // Synthetic data with the exact upstream serialization schema, no game assets.
    using preservation::legacy::json;
    json data = json::object();
    for (auto key : {"0", "10", "50", "70", "90", "200", "220", "230", "250"})
        data[key] = {{"x", 0.0}, {"y", 0.0}, {"z", 0.0}, {"w", 0.0}};
    for (auto key : {"20", "38", "B8", "C0", "C4", "C8", "D0", "1AC", "1B8", "1BC", "210", "214", "218", "240"}) data[key] = 0.0;
    for (auto key : {"30", "34", "40", "80", "84", "88", "BC", "CC", "198", "19C", "1A0", "1A4", "1A8", "1B4", "248", "60", "244", "8C", "B0", "21C", "21D", "268"}) data[key] = 0;
    for (auto key : {"1B0", "1B2"}) data[key] = {{"lr", 0}, {"fb", 0}};
    data["1A0"] = frame;
    data["220"]["x"] = x;
    data["200"]["w"] = 1.0;
    return data;
}
inline preservation::legacy::json join_fixture(const std::string& id) {
    auto j = preservation::legacy::event(preservation::legacy::Type::JoinInstance, id);
    j["name"] = "Synthetic participant"; return j;
}
inline preservation::legacy::json hero_fixture(const std::string& id, std::int64_t hero = 1) {
    auto j = preservation::legacy::event(preservation::legacy::Type::ChangeHero, id);
    j["heroid"] = hero; j["skinid"] = 0; return j;
}
inline preservation::legacy::json position_fixture(const std::string& id, int frame = 1, double x = 0) {
    auto j = preservation::legacy::event(preservation::legacy::Type::PositionUpdate, id);
    j["data"] = movement_fixture(frame, x); return j;
}
