#pragma once
#include <cstdint>
#include <string_view>

// Disc 1.0.1.27578 only. RVAs were identified in an isolated startup capture;
// object layouts are checked again against the child before use.
namespace disc_profile {
inline constexpr std::string_view sha256 = "8d33644f844b81e830c12749371c80a83d26f81b186265897ca5d67f6e7e665d";
inline constexpr uint64_t entity_admin_global = 0x15011e0;
inline constexpr uint64_t entity_admin_vtable = 0x12f54c8;
inline constexpr uint64_t world_vtable = 0x12f4b18;
inline constexpr uint64_t world_initializer = 0x962fc0;
inline constexpr uint64_t world_tick = 0x962fe0;
inline constexpr uint64_t world_advance = 0x964500;
inline constexpr uint64_t package_table = 0x15dc7a0;
inline constexpr uint64_t package_lookup_selection = 0x644937;
inline constexpr uint64_t resource_manager_global = 0x1501240;
inline constexpr uint64_t resource_manager_vtable = 0x12f53d8;
inline constexpr uint64_t map_interface_vtable = 0x12f4e18;
inline constexpr uint64_t map_loader = 0x9732d0;
inline constexpr uint64_t package_loader = 0xc13b70;
inline constexpr uint64_t resource_request = 0x647450;
inline constexpr uint64_t immutable_stu_parse = 0x447970;
inline constexpr uint64_t catalogue_vtable = 0x11c0f60;
inline constexpr uint64_t catalogue_schema = 0x147db60;
inline constexpr uint64_t resource_import_memory = 0x64bfd0;
inline constexpr uint64_t stu_allocator_global = 0x155aef8;
inline constexpr uint64_t stu_allocator_vtable = 0x12791b0;
inline constexpr uint64_t stu_allocator_allocate = 0x437220;
inline constexpr uint64_t missing_voice_catalogue = 0x07a000000000001d;
inline constexpr uint64_t hanamura_map = 0x0800000000000165;
inline constexpr unsigned systems_offset = 0xd8;
inline constexpr unsigned world_state_offset = 0x10;
inline constexpr unsigned wanted_map_offset = 0x18;
inline constexpr unsigned loaded_map_offset = 0x20;
}
