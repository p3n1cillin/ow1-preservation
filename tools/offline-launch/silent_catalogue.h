#pragma once
#include <array>
#include <cstdint>

// Author-written, empty immutable STU v3 resource for the fingerprinted disc.
// Schema identity/layout checksum comes from the client's type registry; no
// voice definitions, recordings or recovered asset bytes are embedded here.
inline std::array<unsigned char, 96> silent_catalogue() {
    std::array<unsigned char, 96> data{};
    auto put = [&](unsigned offset, uint64_t value, unsigned size) {
        for (unsigned n = 0; n < size; ++n) data[offset + n] = static_cast<unsigned char>(value >> (n * 8));
    };
    put(0, 0x53545544, 4); // DUTS
    put(4, 3, 4);          // immutable format version
    put(8, 64, 8);         // metadata table
    put(16, 0xbad42a8d, 4); // native catalogue root type
    put(24, 48, 8);        // empty list header
    put(44, 3, 4);         // observed root enum value
    put(64, 1, 4);         // one root instance, no voice entries
    put(72, 80, 8);        // instance records
    put(80, 16, 4);        // root offset; flags remain zero
    put(88, 0xc247af386814cd10ULL, 8); // native schema checksum
    return data;
}
