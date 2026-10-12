#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <winsock2.h>
#include <windows.h>
#include <userenv.h>
#include <sddl.h>
#include <aclapi.h>
#include <dbghelp.h>
#include <winternl.h>
#include <filesystem>
#include <iostream>
#include <string>
#include <stdexcept>
#include <cstring>
#include <d3d11.h>
#include <dxgi.h>
#include <psapi.h>
#include <wbemidl.h>
#include <bcrypt.h>
#include <vector>
#include <memory>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <atomic>
#include <thread>
#include "disc_profile.h"
#include "silent_catalogue.h"
#include "retail_profile.h"
#include "retail_tls_patch.h"
#include "loopback_bridge.h"

template<typename T> T read_child(HANDLE process, uint64_t address) {
    T value{};
    SIZE_T read = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(address), &value, sizeof(value), &read) || read != sizeof(value))
    {
        const auto error = GetLastError();
        std::ostringstream message; message << "Native memory read failed at 0x" << std::hex << address
            << " (" << std::dec << sizeof(value) << " bytes), Win32=" << error;
        throw std::runtime_error(message.str());
    }
    return value;
}

uint64_t disc_world(HANDLE process, uint64_t image) {
    const auto ea = read_child<uint64_t>(process, image + disc_profile::entity_admin_global);
    if (!ea) return 0;
    if (read_child<uint64_t>(process, ea) != image + disc_profile::entity_admin_vtable)
        throw std::runtime_error("Disc entity admin identity differs");
    struct List { uint64_t address; uint32_t count, capacity; };
    const auto list = read_child<List>(process, ea + disc_profile::systems_offset);
    if (list.count > 128 || list.count > list.capacity || list.capacity > 256 || !list.address)
        throw std::runtime_error("Disc system list bounds differ");
    uint64_t result = 0;
    for (unsigned n = 0; n < list.count; ++n) {
        const auto system = read_child<uint64_t>(process, list.address + n * 8);
        if (read_child<uint64_t>(process, system) == image + disc_profile::world_vtable) {
            if (result || read_child<uint64_t>(process, system + 8) != ea)
                throw std::runtime_error("Disc world ownership differs");
            result = system;
        }
    }
    return result;
}

struct MapPreload { uint64_t callback = 0, completed = 0, voice_handle = 0; };

uint64_t child_function_table_api(HANDLE process, const char* name = "RtlAddFunctionTable") {
    const auto local = GetModuleHandleW(L"ntdll.dll");
    const auto function = GetProcAddress(local, name);
    wchar_t local_path[MAX_PATH]{};
    if (!function || !GetModuleFileNameW(local, local_path, MAX_PATH))
        throw std::runtime_error("Windows function-table API unavailable");
    HMODULE modules[256]{}; DWORD needed = 0;
    if (!EnumProcessModules(process, modules, sizeof(modules), &needed) || needed > sizeof(modules))
        throw std::runtime_error("Disc module inventory failed");
    const auto offset = reinterpret_cast<uint64_t>(function) - reinterpret_cast<uint64_t>(local);
    for (unsigned n = 0; n < needed / sizeof(HMODULE); ++n) {
        wchar_t path[MAX_PATH]{}; MODULEINFO info{};
        if (!GetModuleFileNameExW(process, modules[n], path, MAX_PATH) || _wcsicmp(path, local_path)) continue;
        if (!GetModuleInformation(process, modules[n], &info, sizeof(info)) || offset + 16 > info.SizeOfImage)
            throw std::runtime_error("Disc Windows API bounds differ");
        const auto address = reinterpret_cast<uint64_t>(modules[n]) + offset;
        unsigned char bytes[16]{}; SIZE_T count = 0;
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(address), bytes, sizeof(bytes), &count)
            || count != sizeof(bytes) || memcmp(bytes, function, sizeof(bytes)))
            throw std::runtime_error("Disc Windows function-table API differs");
        return address;
    }
    throw std::runtime_error("Disc Windows runtime module missing");
}

void replace_callback(HANDLE process, uint64_t slot, uint64_t expected, uint64_t replacement) {
    if (read_child<uint64_t>(process, slot) != expected)
        throw std::runtime_error("Disc map callback changed before update");
    DWORD protection = 0, ignored = 0; SIZE_T written = 0;
    if (!VirtualProtectEx(process, reinterpret_cast<void*>(slot), 8, PAGE_READWRITE, &protection))
        throw std::runtime_error("Disc map callback slot protection failed");
    const bool installed = WriteProcessMemory(process, reinterpret_cast<void*>(slot), &replacement, sizeof(replacement), &written)
        && written == sizeof(replacement);
    const bool restored = VirtualProtectEx(process, reinterpret_cast<void*>(slot), 8, protection, &ignored);
    if (!installed || !restored) throw std::runtime_error("Disc map callback slot update failed");
}

MapPreload install_map_preload(HANDLE process, uint64_t image, bool request_voice, bool silent_voice, bool import_catalogue) {
    const auto manager = read_child<uint64_t>(process, image + disc_profile::resource_manager_global);
    if (!manager || read_child<uint64_t>(process, manager) != image + disc_profile::resource_manager_vtable)
        throw std::runtime_error("Disc resource manager identity differs");
    const auto ea = read_child<uint64_t>(process, image + disc_profile::entity_admin_global);
    const auto iface = read_child<uint64_t>(process, ea + 0x130);
    const auto slot = image + disc_profile::map_interface_vtable + 0x48;
    if (!iface || read_child<uint64_t>(process, iface) != image + disc_profile::map_interface_vtable
        || read_child<uint64_t>(process, slot) != image + disc_profile::map_loader)
        throw std::runtime_error("Disc map interface identity differs");
    const unsigned char expected[] = {0x44,0x89,0x4c,0x24,0x20,0x4c,0x89,0x44,0x24,0x18};
    unsigned char actual[sizeof(expected)]{}; SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + disc_profile::package_loader), actual, sizeof(actual), &count)
        || count != sizeof(actual) || memcmp(actual, expected, sizeof(actual)))
        throw std::runtime_error("Disc package loader instructions differ");
    unsigned char data[512]{};
    auto memory = VirtualAllocEx(process, nullptr, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!memory) throw std::runtime_error("Disc preload diagnostic allocation failed");
    const auto control = reinterpret_cast<uint64_t>(memory);
    uint64_t allocator = 0;
    if (import_catalogue) {
        const unsigned char prefix[] = {0x40,0x56,0x57,0x41,0x56,0x48,0x81,0xec,0x80,0,0,0};
        unsigned char bytes[sizeof(prefix)]{};
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + disc_profile::resource_import_memory), bytes, sizeof(bytes), &count)
            || count != sizeof(bytes) || memcmp(bytes, prefix, sizeof(bytes)))
            throw std::runtime_error("Disc memory importer instructions differ");
        allocator = read_child<uint64_t>(process, image + disc_profile::stu_allocator_global);
        if (!allocator || read_child<uint64_t>(process, allocator) != image + disc_profile::stu_allocator_vtable
            || read_child<uint64_t>(process, image + disc_profile::stu_allocator_vtable + 0x30) != image + disc_profile::stu_allocator_allocate)
            throw std::runtime_error("Disc STU allocator identity differs");
        memcpy(data + 128, &disc_profile::missing_voice_catalogue, 8);
        const uint32_t size = static_cast<uint32_t>(silent_catalogue().size());
        memcpy(data + 144, &size, 4); data[148] = 1;
        const uint64_t invalid = ~uint64_t{0}; memcpy(data + 88, &invalid, 8);
        const uint32_t priority = 5;
        const uint64_t globals = 0x0400000000000595, map_definition = 0x04000000000001fa;
        memcpy(data + 160, &invalid, 8); memcpy(data + 168, &invalid, 8);
        memcpy(data + 384 + 0x10, &globals, 8); memcpy(data + 384 + 0x28, &priority, 4);
        memcpy(data + 448 + 0x10, &map_definition, 8); memcpy(data + 448 + 0x28, &priority, 4);
    }
    uint64_t voice_request = 0;
    if (request_voice) {
        const unsigned char prefix_request[] = {0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x6c,0x24,0x10};
        const auto prefix = prefix_request;
        const auto function = disc_profile::resource_request;
        unsigned char bytes[10]{};
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + function), bytes, sizeof(bytes), &count)
            || count != sizeof(bytes) || memcmp(bytes, prefix, sizeof(bytes)))
            throw std::runtime_error("Disc resource request instructions differ");
        // Retain one native request handle for the lifetime of this bounded
        // process. The native loader reports missing metadata itself; no
        // completion flags are supplied by the adapter. The silent branch
        // validates a separate author-written object without registering it as
        // a replacement or reconstructing the original voice definitions.
        const uint64_t invalid = ~uint64_t{0};
        const uint32_t priority = 5;
        memcpy(data, &invalid, 8);
        if (silent_voice) {
            const unsigned char parse_prefix[] = {0x40,0x57,0x48,0x83,0xec,0x50};
            unsigned char checked_bytes[sizeof(parse_prefix)]{};
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + disc_profile::immutable_stu_parse), checked_bytes, sizeof(checked_bytes), &count)
                || count != sizeof(checked_bytes) || memcmp(checked_bytes, parse_prefix, sizeof(checked_bytes)))
                throw std::runtime_error("Disc catalogue parser instructions differ");
            const auto schema = image + disc_profile::catalogue_schema;
            if (read_child<uint64_t>(process, schema + 0x38) != 0xc247af386814cd10ULL
                || read_child<uint32_t>(process, schema + 0x50) != 0xbad42a8d
                || read_child<uint32_t>(process, schema + 0x54) != 3
                || read_child<uint32_t>(process, schema + 0x5c) != 32)
                throw std::runtime_error("Disc silent catalogue schema differs");
            const auto payload = silent_catalogue();
            memcpy(data + 256, payload.data(), payload.size());
        }
        memcpy(data + 16 + 0x10, &disc_profile::missing_voice_catalogue, 8);
        memcpy(data + 16 + 0x28, &priority, 4);
        voice_request = control;
    }
    if (!WriteProcessMemory(process, memory, data, sizeof(data), &count) || count != sizeof(data))
        throw std::runtime_error("Disc preload diagnostic initialization failed");
    // Run native package requests on the thread that already calls LoadMap.
    // Preserve all volatile registers, XMM0-5 and flags; reserve aligned Win64
    // shadow/argument space. Tail-jump to the unchanged native map loader.
    void* remote = VirtualAllocEx(process, nullptr, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remote) throw std::runtime_error("Allocate disc preload callback");
    const auto address = reinterpret_cast<uint64_t>(remote);
    std::vector<unsigned char> code;
    auto emit = [&](std::initializer_list<unsigned char> bytes) { code.insert(code.end(), bytes); };
    auto value = [&](auto data) {
        const auto bytes = reinterpret_cast<const unsigned char*>(&data);
        code.insert(code.end(), bytes, bytes + sizeof(data));
    };
    emit({0x9c,0x50,0x51,0x52,0x41,0x50,0x41,0x51,0x41,0x52,0x41,0x53,0x48,0x81,0xec}); value(uint32_t{0x98});
    for (unsigned reg = 0; reg < 6; ++reg) {
        emit({0x0f,0x11,static_cast<unsigned char>(0x84 + reg * 8),0x24}); value(uint32_t{0x30 + reg * 16});
    }
    size_t registration_failure = 0;
    if (silent_voice) {
        // This callback calls deeper native code. Register its stack allocation
        // with Windows so native exception/stack walking can traverse it. Keep
        // code and metadata allocated until process exit.
        emit({0x48,0xb9}); value(address + 1024);
        emit({0xba}); value(uint32_t{1});
        emit({0x49,0xb8}); value(address);
        emit({0x48,0xb8}); value(child_function_table_api(process)); emit({0xff,0xd0});
        emit({0x48,0xb9}); value(control + 108); emit({0x89,0x01,0x85,0xc0,0x0f,0x84});
        registration_failure = code.size(); value(int32_t{0});
    }
    if (voice_request) {
        if (silent_voice) {
            // First validate the author-written payload using the native
            // in-place STU parser. The buffer lives until this child ends and
            // is never passed off as an original hash-matching asset.
            emit({0x48,0xb9}); value(control + 256);
            emit({0x48,0xb8}); value(image + disc_profile::immutable_stu_parse); emit({0xff,0xd0});
            emit({0x48,0xb9}); value(control + 96); emit({0x48,0x89,0x01});
        }
        emit({0x48,0xb9}); value(voice_request);
        emit({0x48,0xba}); value(voice_request + 16);
        emit({0x48,0xb8}); value(image + disc_profile::resource_request); emit({0xff,0xd0});
        emit({0x48,0xb9}); value(control + 84); emit({0x89,0x01});
        if (import_catalogue) {
            std::vector<size_t> request_failures;
            auto reject = [&](unsigned char condition) {
                emit({0x0f,condition}); request_failures.push_back(code.size()); value(int32_t{0});
            };
            emit({0x85,0xc0}); reject(0x88); // negative native request status
            emit({0x48,0xb9}); value(control); emit({0x48,0x8b,0x11,0x48,0x83,0xe2,0xc0,0x48,0x85,0xd2}); reject(0x84);
            emit({0x48,0xb9}); value(disc_profile::missing_voice_catalogue);
            emit({0x48,0x39,0x4a,0x10}); reject(0x85);
            // Use the STU allocator that its native destructor later frees.
            emit({0x48,0xb9}); value(allocator);
            emit({0xba}); value(uint32_t{96}); emit({0x41,0xb8}); value(uint32_t{16}); emit({0x45,0x31,0xc9});
            emit({0x48,0xb8}); value(image + disc_profile::stu_allocator_allocate); emit({0xff,0xd0});
            emit({0x49,0x89,0xc2});
            emit({0x48,0xb9}); value(control + 136); emit({0x48,0x89,0x01});
            // A null allocation must not reach the native importer.
            emit({0x48,0x85,0xc0,0x0f,0x84}); const auto failed = code.size(); value(int32_t{0});
            const auto payload = silent_catalogue();
            for (unsigned offset = 0; offset < payload.size(); offset += 8) {
                uint64_t word = 0; memcpy(&word, payload.data() + offset, 8);
                emit({0x48,0xb8}); value(word); emit({0x49,0x89,0x42,static_cast<unsigned char>(offset)});
            }
            emit({0x48,0xb9}); value(control); emit({0x48,0x8b,0x11,0x48,0x83,0xe2,0xc0});
            emit({0x49,0xb8}); value(control + 128);
            emit({0x48,0xb9}); value(control + 88);
            emit({0x48,0xb8}); value(image + disc_profile::resource_import_memory); emit({0xff,0xd0});
            emit({0xe9}); const auto complete = code.size(); value(int32_t{0});
            const auto bad = static_cast<int32_t>(code.size() - failed - 4); memcpy(code.data() + failed, &bad, 4);
            for (const auto jump : request_failures) {
                const auto displacement = static_cast<int32_t>(code.size() - jump - 4);
                memcpy(code.data() + jump, &displacement, 4);
            }
            emit({0xb8}); value(int32_t{-4});
            const auto done = static_cast<int32_t>(code.size() - complete - 4); memcpy(code.data() + complete, &done, 4);
            emit({0x48,0xb9}); value(control + 112); emit({0x89,0x01});
            // Resolve the real definitions through the unchanged file-backed
            // request API. No definition bytes or readiness flags are supplied.
            for (auto [output, request, status] : {std::array<uint64_t,3>{160,384,116}, std::array<uint64_t,3>{168,448,120}}) {
                emit({0x48,0xb9}); value(control + output);
                emit({0x48,0xba}); value(control + request);
                emit({0x48,0xb8}); value(image + disc_profile::resource_request); emit({0xff,0xd0});
                emit({0x48,0xb9}); value(control + status); emit({0x89,0x01});
            }
        }
    }
    for (uint64_t pack : {0x06e0000000000079ULL, uint64_t{0}}) {
        for (uint32_t priority : {3U,5U}) {
            emit({0x48,0xb9}); value(manager);
            if (pack) { emit({0x48,0xba}); value(pack); }
            else { emit({0x48,0x8b,0x94,0x24}); value(uint32_t{0xb8}); }
            emit({0x45,0x31,0xc0,0x45,0x31,0xc9,0xc7,0x44,0x24,0x20}); value(priority);
            emit({0x48,0xb8}); value(image + disc_profile::package_loader); emit({0xff,0xd0});
        }
    }
    if (registration_failure) {
        const auto displacement = static_cast<int32_t>(code.size() - registration_failure - 4);
        memcpy(code.data() + registration_failure, &displacement, 4);
    }
    emit({0x48,0xb8}); value(control + 80); emit({0xc7,0x00,0x01,0,0,0});
    for (unsigned reg = 0; reg < 6; ++reg) {
        emit({0x0f,0x10,static_cast<unsigned char>(0x84 + reg * 8),0x24}); value(uint32_t{0x30 + reg * 16});
    }
    emit({0x48,0x81,0xc4}); value(uint32_t{0x98});
    emit({0x41,0x5b,0x41,0x5a,0x41,0x59,0x41,0x58,0x5a,0x59,0x58,0x9d,0xff,0x25,0,0,0,0});
    value(image + disc_profile::map_loader);
    if (silent_voice) {
        if (code.size() > 1024) throw std::runtime_error("Disc callback overlaps unwind metadata");
        const uint32_t table[] = {0, static_cast<uint32_t>(code.size()), 1056};
        // Version 1, 19-byte prologue, UWOP_ALLOC_LARGE = 216 bytes:
        // eight volatile/flags pushes (64) plus sub rsp,152. No nonvolatile
        // registers are modified by this wrapper.
        const unsigned char unwind[] = {1,19,2,0,19,1,27,0};
        if (!WriteProcessMemory(process, reinterpret_cast<void*>(address + 1024), table, sizeof(table), &count)
            || count != sizeof(table)
            || !WriteProcessMemory(process, reinterpret_cast<void*>(address + 1056), unwind, sizeof(unwind), &count)
            || count != sizeof(unwind)) throw std::runtime_error("Disc callback unwind metadata write failed");
    }
    DWORD protection = 0; SIZE_T written = 0;
    if (!WriteProcessMemory(process, remote, code.data(), code.size(), &written) || written != code.size()
        || !VirtualProtectEx(process, remote, 4096, PAGE_EXECUTE_READ, &protection)
        || !FlushInstructionCache(process, remote, code.size()))
        throw std::runtime_error("Disc preload callback installation failed");
    replace_callback(process, slot, image + disc_profile::map_loader, address);
    std::cout << "Installed guarded native map-package preload callback." << std::endl;
    if (voice_request) std::cout << (silent_voice
        ? (import_catalogue ? "Experimental author-written silent catalogue submitted through native memory importer."
                            : "Experimental empty catalogue parser probe; candidate is not registered as a replacement.")
        : "Native missing-voice request enabled; completion/failure remains native.") << std::endl;
    return {address, control + 80, voice_request};
}

uint64_t install_world_advance(HANDLE process, uint64_t image, uint64_t world) {
    const auto slot = image + disc_profile::world_vtable + 0x68;
    if (read_child<uint64_t>(process, world) != image + disc_profile::world_vtable
        || read_child<uint64_t>(process, slot) != image + disc_profile::world_tick)
        throw std::runtime_error("Disc world tick identity differs");
    const unsigned char expected[] = {0x48,0x89,0x74,0x24,0x18,0x57,0x48,0x83,0xec,0x20};
    unsigned char actual[sizeof(expected)]{}; SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + disc_profile::world_advance), actual, sizeof(actual), &count)
        || count != sizeof(actual) || memcmp(expected, actual, sizeof(actual)))
        throw std::runtime_error("Disc world advance instructions differ");
    // The beta adapter explicitly calls its native state-change function in
    // states 5/6. Keep this experiment separate: it provides no replicated
    // entities, authenticated session or gameplay state.
    std::vector<unsigned char> code;
    auto emit = [&](std::initializer_list<unsigned char> bytes) { code.insert(code.end(), bytes); };
    auto value = [&](auto data) {
        const auto bytes = reinterpret_cast<const unsigned char*>(&data);
        code.insert(code.end(), bytes, bytes + sizeof(data));
    };
    emit({0x9c,0x50,0x51,0x52,0x41,0x50,0x41,0x51,0x41,0x52,0x41,0x53,0x48,0x81,0xec}); value(uint32_t{0x98});
    for (unsigned reg = 0; reg < 6; ++reg) {
        emit({0x0f,0x11,static_cast<unsigned char>(0x84 + reg * 8),0x24}); value(uint32_t{0x30 + reg * 16});
    }
    emit({0x80,0x79,0x10,0x05,0x74,0x06,0x80,0x79,0x10,0x06,0x75,0x0c});
    emit({0x48,0xb8}); value(image + disc_profile::world_advance); emit({0xff,0xd0});
    for (unsigned reg = 0; reg < 6; ++reg) {
        emit({0x0f,0x10,static_cast<unsigned char>(0x84 + reg * 8),0x24}); value(uint32_t{0x30 + reg * 16});
    }
    emit({0x48,0x81,0xc4}); value(uint32_t{0x98});
    emit({0x41,0x5b,0x41,0x5a,0x41,0x59,0x41,0x58,0x5a,0x59,0x58,0x9d,0xff,0x25,0,0,0,0});
    value(image + disc_profile::world_tick);
    auto memory = VirtualAllocEx(process, nullptr, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    DWORD protection = 0;
    if (!memory || !WriteProcessMemory(process, memory, code.data(), code.size(), &count) || count != code.size()
        || !VirtualProtectEx(process, memory, 4096, PAGE_EXECUTE_READ, &protection)
        || !FlushInstructionCache(process, memory, code.size()))
        throw std::runtime_error("Disc world advance callback installation failed");
    const auto address = reinterpret_cast<uint64_t>(memory);
    replace_callback(process, slot, image + disc_profile::world_tick, address);
    std::cout << "Experimental native world-stage advancement enabled; replication is not supplied." << std::endl;
    return address;
}

bool map_probe(HANDLE process, uint64_t image, bool omit_speech, bool preload, bool request_voice, bool advance_stages, bool silent_voice, bool import_catalogue) {
    // This changes only a local world request; all network capabilities remain
    // absent. It does not create an account, authenticated session or player.
    const unsigned char expected[] = {0xc6,0x41,0x10,0x02,0xb0,0x01,0xc3};
    unsigned char actual[sizeof(expected)]{};
    SIZE_T read = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + disc_profile::world_initializer), actual, sizeof(actual), &read)
        || read != sizeof(actual) || memcmp(actual, expected, sizeof(actual)))
        throw std::runtime_error("Disc world initializer bytes differ");
    const auto world = disc_world(process, image);
    if (!world || read_child<unsigned char>(process, world + disc_profile::world_state_offset) != 2
        || read_child<uint64_t>(process, world + disc_profile::wanted_map_offset)
        || read_child<uint64_t>(process, world + disc_profile::loaded_map_offset))
        throw std::runtime_error("Disc world is not idle; map probe refused");
    if (omit_speech) {
        // Native lookup treats an absent speech row as optional; its pack
        // constructor leaves that resource handle at -1. Retain the allocation
        // so existing lookups remain valid. No loader-ready flags are changed.
        const unsigned char selection[] = {0x48,0x8d,0x5e,0x50,0x40,0x84,0xff,0x75,0x04,0x48,0x8d,0x5e,0x38};
        unsigned char actual_selection[sizeof(selection)]{};
        SIZE_T read = 0;
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + disc_profile::package_lookup_selection),
                               actual_selection, sizeof(selection), &read)
            || read != sizeof(selection) || memcmp(selection, actual_selection, sizeof(selection)))
            throw std::runtime_error("Disc speech lookup instructions differ");
        struct SpeechList { uint64_t address; uint32_t count, capacity; };
        const auto location = image + disc_profile::package_table + 0x50;
        const auto speech = read_child<SpeechList>(process, location);
        if (!speech.address || speech.count != 729 || speech.capacity != 729)
            throw std::runtime_error("Disc speech manifest bounds differ");
        for (unsigned n = 0; n < speech.count; ++n) {
            const auto identity = read_child<uint64_t>(process, speech.address + n * 72 + 32);
            if ((identity & 0x300000000000ULL) != 0x100000000000ULL)
                throw std::runtime_error("Disc speech entry identity differs");
        }
        const uint32_t empty = 0;
        SIZE_T written = 0;
        if (!WriteProcessMemory(process, reinterpret_cast<void*>(location + 8), &empty, sizeof(empty), &written)
            || written != sizeof(empty)) throw std::runtime_error("Disc optional speech diagnostic failed");
        std::cout << "Optional speech variants omitted in this process; original files unchanged." << std::endl;
    }
    auto callback = preload ? install_map_preload(process, image, request_voice, silent_voice, import_catalogue) : MapPreload{};
    auto stage_callback = advance_stages ? install_world_advance(process, image, world) : uint64_t{0};
    const auto map = disc_profile::hanamura_map;
    SIZE_T written = 0;
    if (!WriteProcessMemory(process, reinterpret_cast<void*>(world + disc_profile::wanted_map_offset), &map, sizeof(map), &written)
        || written != sizeof(map)) throw std::runtime_error("Disc map request failed");
    std::cout << "Experimental offline world request: map=0x" << std::hex << map << std::dec << std::endl;
    int previous = -1;
    uint32_t previous_voice_flags = 0;
    uint32_t previous_definition_flags[2]{};
    const unsigned iterations = advance_stages ? 120 : 600;
    for (unsigned n = 0; n < iterations; ++n) {
        if (WaitForSingleObject(process, 500) == WAIT_OBJECT_0) return false;
        if (callback.callback && read_child<uint32_t>(process, callback.completed)) {
            replace_callback(process, image + disc_profile::map_interface_vtable + 0x48, callback.callback, image + disc_profile::map_loader);
            callback.callback = 0;
            std::cout << "Native preload requests submitted; original map callback restored." << std::endl;
        }
        const auto state = read_child<unsigned char>(process, world + disc_profile::world_state_offset);
        if (import_catalogue && read_child<uint32_t>(process, callback.completed)) {
            for (unsigned index = 0; index < 2; ++index) {
                const auto status = read_child<int32_t>(process, callback.voice_handle + 116 + index * 4);
                if (status < 0) throw std::runtime_error("Native real-definition request rejected");
                const auto handle = read_child<uint64_t>(process, callback.voice_handle + 160 + index * 8);
                const auto descriptor = handle & ~uint64_t{63};
                const uint64_t guid = index ? 0x04000000000001fa : 0x0400000000000595;
                if (handle == ~uint64_t{0} || !descriptor || read_child<uint64_t>(process, descriptor + 16) != guid)
                    throw std::runtime_error("Native definition handle identity differs");
                const auto flags = read_child<uint32_t>(process, descriptor + 8);
                if ((flags & 63) != (handle & 63)) throw std::runtime_error("Native definition handle generation differs");
                if (flags != previous_definition_flags[index]) {
                    std::cout << "Native definition guid=0x" << std::hex << guid << " flags=0x" << flags
                        << " object=0x" << read_child<uint64_t>(process, descriptor) << std::dec << std::endl;
                    previous_definition_flags[index] = flags;
                }
            }
        }
        if (silent_voice && callback.voice_handle && read_child<uint32_t>(process, callback.completed)) {
            if (!read_child<uint32_t>(process, callback.voice_handle + 108))
                throw std::runtime_error("Disc callback unwind registration failed; parser was not called");
            const auto root = read_child<uint64_t>(process, callback.voice_handle + 96);
            if (!root || read_child<uint64_t>(process, root) != image + disc_profile::catalogue_vtable)
                throw std::runtime_error("Native parser did not construct the empty catalogue root");
            const auto entries = read_child<uint64_t>(process, root + 8);
            if (!entries || read_child<uint32_t>(process, entries) != 0)
                throw std::runtime_error("Native empty catalogue entry list differs");
            if (!previous_voice_flags)
                std::cout << "Native parser constructed the author-written empty catalogue root; no voice entries supplied." << std::endl;
            const auto status = read_child<int32_t>(process, callback.voice_handle + 84);
            if (status < 0) throw std::runtime_error("Native original catalogue request rejected: " + std::to_string(status));
            const auto handle = read_child<uint64_t>(process, callback.voice_handle + (import_catalogue ? 88 : 0));
            if (import_catalogue && read_child<int32_t>(process, callback.voice_handle + 112) < 0)
                throw std::runtime_error("Native catalogue memory importer rejected candidate");
            const auto descriptor = handle & ~uint64_t{63};
            if (handle == ~uint64_t{0} || !descriptor || read_child<uint64_t>(process, descriptor + 0x10) != disc_profile::missing_voice_catalogue)
                throw std::runtime_error("Native silent catalogue handle identity differs");
            const auto flags = read_child<uint32_t>(process, descriptor + 8);
            if ((flags & 63) != (handle & 63)) throw std::runtime_error("Native silent catalogue handle generation differs");
            if (flags != previous_voice_flags) {
                std::cout << "Catalogue native request result=" << status << " flags=0x" << std::hex << flags
                    << " object=0x" << read_child<uint64_t>(process, descriptor) << std::dec << std::endl;
                previous_voice_flags = flags;
            }
            if (!import_catalogue) {
                std::cout << "Empty catalogue schema validated; replacement not installed. Native storage/importer integration remains unimplemented." << std::endl;
                return true;
            }
            const auto object = read_child<uint64_t>(process, descriptor);
            if ((flags & 0x10000) && !(flags & 0x8000) && object) {
                if (read_child<uint64_t>(process, object) != image + disc_profile::catalogue_vtable
                    || object != read_child<uint64_t>(process, callback.voice_handle + 136) + 16)
                    throw std::runtime_error("Imported catalogue native root identity differs");
                std::cout << "Native importer published a loaded silent catalogue object; original voice content remains absent." << std::endl;
                silent_voice = false;
            }
        }
        if (stage_callback && state >= 7) {
            replace_callback(process, image + disc_profile::world_vtable + 0x68, stage_callback, image + disc_profile::world_tick);
            stage_callback = 0;
            std::cout << "Native world-stage callbacks dispatched; original world tick restored." << std::endl;
        }
        if (state != previous) {
            std::cout << "Disc world state=" << unsigned(state) << " loaded_map=0x" << std::hex
                << read_child<uint64_t>(process, world + disc_profile::loaded_map_offset) << std::dec << std::endl;
            previous = state;
        }
        if (n && n % 120 == 0) std::cout << "Map probe still waiting: state=" << unsigned(state) << std::endl;
    }
    return false;
}

std::string sha256(const std::filesystem::path& path) {
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    BCRYPT_HASH_HANDLE hash = nullptr;
    if (BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_SHA256_ALGORITHM, nullptr, 0) < 0)
        throw std::runtime_error("SHA256 provider unavailable");
    if (BCryptCreateHash(algorithm, &hash, nullptr, 0, nullptr, 0, 0) < 0) {
        BCryptCloseAlgorithmProvider(algorithm, 0); throw std::runtime_error("SHA256 initialization failed");
    }
    std::ifstream file(path, std::ios::binary);
    char buffer[65536];
    bool good = static_cast<bool>(file);
    while (file.read(buffer, sizeof(buffer)) || file.gcount())
        good &= BCryptHashData(hash, reinterpret_cast<PUCHAR>(buffer), static_cast<ULONG>(file.gcount()), 0) >= 0;
    unsigned char digest[32]{};
    good &= file.eof() && BCryptFinishHash(hash, digest, sizeof(digest), 0) >= 0;
    BCryptDestroyHash(hash); BCryptCloseAlgorithmProvider(algorithm, 0);
    if (!good) throw std::runtime_error("Executable SHA256 read failed");
    std::ostringstream result;
    for (const auto byte : digest) result << std::hex << std::setw(2) << std::setfill('0') << static_cast<unsigned>(byte);
    return result.str();
}

// Restore the exact scoped DACL after the job has been stopped, including on errors.
struct ScopedAcl {
    std::wstring path;
    PSECURITY_DESCRIPTOR descriptor = nullptr;
    PACL acl = nullptr;
    bool changed = false;
    explicit ScopedAcl(const std::wstring& name) : path(name) {
        const auto status = GetNamedSecurityInfoW(path.c_str(), SE_FILE_OBJECT, DACL_SECURITY_INFORMATION,
                                                 nullptr, nullptr, &acl, nullptr, &descriptor);
        if (status) throw std::runtime_error("Read original scoped ACL: " + std::to_string(status));
    }
    void restore() noexcept {
        if (changed) {
            SECURITY_DESCRIPTOR_CONTROL control = 0; DWORD revision = 0;
            GetSecurityDescriptorControl(descriptor, &control, &revision);
            const auto flags = DACL_SECURITY_INFORMATION | ((control & SE_DACL_PROTECTED)
                ? PROTECTED_DACL_SECURITY_INFORMATION : UNPROTECTED_DACL_SECURITY_INFORMATION);
            const auto status = SetNamedSecurityInfoW(path.data(), SE_FILE_OBJECT, flags, nullptr, nullptr, acl, nullptr);
            if (status) std::cerr << "Scoped ACL restoration failed: " << status << std::endl;
            // SetNamedSecurityInfo removes inherited temporary grants from
            // children, but converts legacy descriptors to auto inheritance.
            // Restore the captured descriptor's exact control bits afterward.
            if (!status) {
                // The legacy setter derives AUTO_INHERITED from the request
                // bit, rather than preserving AUTO_INHERITED by itself.
                if (!SetSecurityDescriptorControl(descriptor, SE_DACL_AUTO_INHERIT_REQ,
                        (control & SE_DACL_AUTO_INHERITED) ? SE_DACL_AUTO_INHERIT_REQ : 0)
                    || !SetFileSecurityW(path.c_str(), DACL_SECURITY_INFORMATION, descriptor))
                    std::cerr << "Scoped ACL control restoration failed: " << GetLastError() << std::endl;
            }
            changed = false;
        }
    }
    ~ScopedAcl() {
        restore();
        if (descriptor) LocalFree(descriptor);
    }
};

struct ScopedAcls {
    std::vector<std::unique_ptr<ScopedAcl>> entries;
    ~ScopedAcls() {
        // Restore parents before separately captured children. Do not depend
        // on the vector implementation's element destruction order.
        for (auto& entry : entries) entry->restore();
    }
};

void checked(bool ok, const char* label) {
    if (!ok) throw std::runtime_error(std::string(label) + ": " + std::to_string(GetLastError()));
}
void allow(PSID sid, const std::wstring& path, DWORD rights, DWORD inheritance) {
    PACL old = nullptr, updated = nullptr;
    PSECURITY_DESCRIPTOR descriptor = nullptr;
    DWORD status = GetNamedSecurityInfoW(path.c_str(), SE_FILE_OBJECT, DACL_SECURITY_INFORMATION,
                                        nullptr, nullptr, &old, nullptr, &descriptor);
    if (status) throw std::runtime_error("Read scoped ACL: " + std::to_string(status));
    EXPLICIT_ACCESSW access{};
    access.grfAccessPermissions = rights;
    access.grfAccessMode = GRANT_ACCESS;
    access.grfInheritance = inheritance;
    access.Trustee.TrusteeForm = TRUSTEE_IS_SID;
    access.Trustee.TrusteeType = TRUSTEE_IS_UNKNOWN;
    access.Trustee.ptstrName = static_cast<LPWSTR>(sid);
    status = SetEntriesInAclW(1, &access, old, &updated);
    if (!status) status = SetNamedSecurityInfoW(const_cast<LPWSTR>(path.c_str()), SE_FILE_OBJECT,
                                               DACL_SECURITY_INFORMATION, nullptr, nullptr, updated, nullptr);
    if (updated) LocalFree(updated);
    LocalFree(descriptor);
    if (status) throw std::runtime_error("Grant scoped ACL: " + std::to_string(status));
}
int network_probe() {
    HANDLE token = nullptr;
    checked(OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token), "Open token");
    DWORD is_container = 0, size = 0;
    checked(GetTokenInformation(token, TokenIsAppContainer, &is_container, sizeof(is_container), &size), "Container token");
    CloseHandle(token);
    WSADATA wsa{};
    if (WSAStartup(MAKEWORD(2, 2), &wsa)) return 3;
    SOCKET socket_handle = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in address{};
    address.sin_family = AF_INET; address.sin_port = htons(443);
    // Public non-Blizzard endpoint: a successful connection fails the isolation test.
    address.sin_addr.s_addr = htonl(0x01010101);
    DWORD timeout = 3000;
    setsockopt(socket_handle, SOL_SOCKET, SO_SNDTIMEO, reinterpret_cast<const char*>(&timeout), sizeof(timeout));
    const int result = connect(socket_handle, reinterpret_cast<sockaddr*>(&address), sizeof(address));
    const int error = WSAGetLastError();
    closesocket(socket_handle); WSACleanup();
    std::cout << "app_container=" << is_container << " connect_result=" << result << " wsa_error=" << error << std::endl;
    return is_container && result == SOCKET_ERROR && error == WSAEACCES ? 0 : 4;
}
int graphics_probe() {
    CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    IWbemLocator* locator = nullptr;
    auto wmi_result = CoCreateInstance(CLSID_WbemLocator, nullptr, CLSCTX_INPROC_SERVER, IID_IWbemLocator, reinterpret_cast<void**>(&locator));
    std::cout << "WMI locator HRESULT=0x" << std::hex << wmi_result << std::endl;
    if (locator) {
        IWbemServices* services = nullptr;
        BSTR ns = SysAllocString(L"ROOT\\CIMV2");
        wmi_result = locator->ConnectServer(ns, nullptr, nullptr, nullptr, 0, nullptr, nullptr, &services);
        std::cout << "WMI ConnectServer HRESULT=0x" << std::hex << wmi_result << std::endl;
        SysFreeString(ns); if (services) services->Release(); locator->Release();
    }
    CoUninitialize();
    IDXGIFactory1* factory = nullptr;
    const auto factory_result = CreateDXGIFactory1(__uuidof(IDXGIFactory1), reinterpret_cast<void**>(&factory));
    std::cout << "CreateDXGIFactory1 HRESULT=0x" << std::hex << factory_result << std::endl;
    if (factory) factory->Release();
    for (const auto driver : {D3D_DRIVER_TYPE_HARDWARE, D3D_DRIVER_TYPE_WARP}) {
        ID3D11Device* device = nullptr;
        D3D_FEATURE_LEVEL level{};
        const auto result = D3D11CreateDevice(nullptr, driver, nullptr, 0, nullptr, 0, D3D11_SDK_VERSION, &device, &level, nullptr);
        std::cout << "D3D11 driver=" << driver << " HRESULT=0x" << std::hex << result << " feature=0x" << level << std::endl;
        if (device) device->Release();
    }
    return 0;
}
PROCESS_INFORMATION launch(PSID sid, const std::wstring& exe, const std::wstring& extra, bool debug = false,
                           const std::wstring& working_directory = L"") {
    SIZE_T bytes = 0;
    InitializeProcThreadAttributeList(nullptr, 1, 0, &bytes);
    auto attributes = static_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(HeapAlloc(GetProcessHeap(), 0, bytes));
    checked(attributes != nullptr, "Allocate attributes");
    checked(InitializeProcThreadAttributeList(attributes, 1, 0, &bytes), "Initialize attributes");
    SECURITY_CAPABILITIES capabilities{};
    capabilities.AppContainerSid = sid; // No Internet, LAN, or other capabilities.
    checked(UpdateProcThreadAttribute(attributes, 0, PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES,
                                      &capabilities, sizeof(capabilities), nullptr, nullptr), "Set capabilities");
    STARTUPINFOEXW startup{};
    startup.StartupInfo.cb = sizeof(startup);
    startup.lpAttributeList = attributes;
    PROCESS_INFORMATION process{};
    auto command = L"\"" + exe + L"\" " + extra;
    const auto directory = working_directory.empty() ? std::filesystem::path(exe).parent_path().wstring() : working_directory;
    const bool success = CreateProcessW(exe.c_str(), command.data(), nullptr, nullptr, FALSE,
                                       EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED | (debug ? DEBUG_ONLY_THIS_PROCESS : 0), nullptr,
                                       directory.c_str(), &startup.StartupInfo, &process);
    const auto error = GetLastError();
    DeleteProcThreadAttributeList(attributes); HeapFree(GetProcessHeap(), 0, attributes);
    SetLastError(error); checked(success, "Create isolated process");
    return process;
}
DWORD debug_run(PROCESS_INFORMATION& child, const std::filesystem::path& folder,
                const std::atomic<bool>* completed = nullptr) {
    DWORD64 image_base = 0;
    bool initial_break = true;
    unsigned exceptions = 0;
    const auto start = GetTickCount64();
    while (GetTickCount64() - start < (completed ? 480000 : 60000)) {
        if (completed && completed->load()) {
            TerminateProcess(child.hProcess, 3); return 3;
        }
        DEBUG_EVENT event{};
        if (!WaitForDebugEvent(&event, 1000)) continue;
        DWORD continuation = DBG_CONTINUE;
        if (event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT) {
            image_base = reinterpret_cast<DWORD64>(event.u.CreateProcessInfo.lpBaseOfImage);
            if (event.u.CreateProcessInfo.hFile) CloseHandle(event.u.CreateProcessInfo.hFile);
        } else if (event.dwDebugEventCode == LOAD_DLL_DEBUG_EVENT) {
            if (event.u.LoadDll.hFile) CloseHandle(event.u.LoadDll.hFile);
        } else if (event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT) {
            auto& record = event.u.Exception.ExceptionRecord;
            const auto address = reinterpret_cast<DWORD64>(record.ExceptionAddress);
            if (exceptions++ < 8 || !event.u.Exception.dwFirstChance)
                std::cout << "Exception code=0x" << std::hex << record.ExceptionCode << " RVA=0x"
                          << (address - image_base) << " first_chance=" << std::dec << event.u.Exception.dwFirstChance << std::endl;
            continuation = DBG_EXCEPTION_NOT_HANDLED;
            if (initial_break && record.ExceptionCode == EXCEPTION_BREAKPOINT) {
                continuation = DBG_CONTINUE; initial_break = false;
            } else if (!event.u.Exception.dwFirstChance) {
                HANDLE thread = OpenThread(THREAD_GET_CONTEXT | THREAD_QUERY_INFORMATION, FALSE, event.dwThreadId);
                CONTEXT context{}; context.ContextFlags = CONTEXT_ALL;
                if (thread && GetThreadContext(thread, &context)) {
                    std::cout << std::hex << "RIP=0x" << context.Rip << " RAX=0x" << context.Rax
                              << " RCX=0x" << context.Rcx << " RDX=0x" << context.Rdx << " RSP=0x" << context.Rsp << std::endl;
                    EXCEPTION_POINTERS pointers{&record, &context};
                    MINIDUMP_EXCEPTION_INFORMATION info{event.dwThreadId, &pointers, FALSE};
                    const auto path = folder / (L"startup-" + std::to_wstring(child.dwProcessId) + L".dmp");
                    HANDLE file = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
                    if (file != INVALID_HANDLE_VALUE) {
                        const bool ok = MiniDumpWriteDump(child.hProcess, child.dwProcessId, file,
                            static_cast<MINIDUMP_TYPE>(MiniDumpWithFullMemory | MiniDumpWithThreadInfo), &info, nullptr, nullptr);
                        std::wcout << L"Crash dump " << (ok ? L"saved: " : L"failed: ") << path << std::endl;
                        CloseHandle(file);
                    }
                }
                if (thread) CloseHandle(thread);
            }
        } else if (event.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT) {
            const auto code = event.u.ExitProcess.dwExitCode;
            ContinueDebugEvent(event.dwProcessId, event.dwThreadId, continuation);
            return code;
        }
        ContinueDebugEvent(event.dwProcessId, event.dwThreadId, continuation);
    }
    TerminateProcess(child.hProcess, 1);
    return 1;
}
#include "retail_world_probe.h"
#include "retail_ca_probe.h"
#include "retail_lobby_key.h"
#include "retail_tls_observer.h"

int wmain(int argc, wchar_t** argv) {
    if (argc == 2 && std::wstring(argv[1]) == L"--child-probe") return network_probe();
    if (argc == 2 && std::wstring(argv[1]) == L"--graphics-probe") return graphics_probe();
    if (argc >= 4 && std::wstring(argv[1]) == L"--loopback-bridge") return loopback_bridge::run_container(argc, argv);
    // --retail-private [--forward PORT[:HOSTPORT]]... [-- CLIENT_ARGS...]
    std::vector<loopback_bridge::Forward> forwards;
    std::wstring client_arguments;
    DWORD private_run_ms = INFINITE;
    std::string trust_ca_pem;
    bool observe_tls = false;
    bool trust_socket_ca = false;
    std::string lobby_public_modulus;
    const bool retail_private = argc > 2 && std::wstring(argv[2]) == L"--retail-private";
    if (retail_private) {
        try {
            int n = 3;
            for (; n < argc && std::wstring(argv[n]) != L"--"; ++n) {
                if (std::wstring(argv[n]) == L"--trust-lobby-key" && n + 1 < argc) {
                    if (!lobby_public_modulus.empty()) throw std::runtime_error("Specify own lobby public modulus once");
                    const std::filesystem::path path = argv[++n];
                    if (!std::filesystem::is_regular_file(path) || std::filesystem::file_size(path) != 256)
                        throw std::runtime_error("Lobby public modulus requires exactly 256 little-endian bytes");
                    std::ifstream input(path, std::ios::binary);
                    lobby_public_modulus.assign(std::istreambuf_iterator<char>(input), {});
                    if (lobby_public_modulus.size() != 256 || !(static_cast<unsigned char>(lobby_public_modulus[0]) & 1)
                        || !(static_cast<unsigned char>(lobby_public_modulus[255]) & 0x80))
                        throw std::runtime_error("Lobby public modulus must be odd and exactly 2048 bits");
                    continue;
                }
                if (std::wstring(argv[n]) == L"--trust-socket-ca") {
                    if (trust_socket_ca) throw std::runtime_error("Specify native socket CA installation once");
                    trust_socket_ca = true; continue;
                }
                if (std::wstring(argv[n]) == L"--observe-tls") {
                    if (observe_tls) throw std::runtime_error("Specify TLS observation once");
                    observe_tls = true; continue;
                }
                if (std::wstring(argv[n]) == L"--trust-ca" && n + 1 < argc) {
                    if (!trust_ca_pem.empty()) throw std::runtime_error("Specify one public CA certificate");
                    const std::filesystem::path certificate = argv[++n];
                    if (!std::filesystem::is_regular_file(certificate) || std::filesystem::file_size(certificate) > 16384)
                        throw std::runtime_error("CA probe requires a bounded public PEM certificate");
                    std::ifstream input(certificate, std::ios::binary);
                    trust_ca_pem.assign(std::istreambuf_iterator<char>(input), {});
                    const std::string begin = "-----BEGIN CERTIFICATE-----", end = "-----END CERTIFICATE-----";
                    const auto first = trust_ca_pem.find(begin), last = trust_ca_pem.find(end);
                    if (trust_ca_pem.size() > 16384 || first == std::string::npos || last == std::string::npos || last <= first
                        || trust_ca_pem.find(begin, first + begin.size()) != std::string::npos
                        || trust_ca_pem.find(end, last + end.size()) != std::string::npos
                        || trust_ca_pem.find("PRIVATE KEY") != std::string::npos || trust_ca_pem.find('\0') != std::string::npos)
                        throw std::runtime_error("CA probe accepts one public PEM certificate, without private keys");
                    continue;
                }
                if (std::wstring(argv[n]) == L"--run-for" && n + 1 < argc) {
                    const std::wstring seconds = argv[++n];
                    if (seconds.empty() || seconds.size() > 4 || seconds.find_first_not_of(L"0123456789") != std::wstring::npos)
                        throw std::runtime_error("Private diagnostic duration must be 1..3600 seconds");
                    const auto value = std::stoul(seconds);
                    if (!value || value > 3600 || private_run_ms != INFINITE)
                        throw std::runtime_error("Private diagnostic duration must be specified once, in 1..3600 seconds");
                    private_run_ms = value * 1000;
                    continue;
                }
                if (std::wstring(argv[n]) != L"--forward" || n + 1 >= argc) throw std::runtime_error("Expected --forward PORT[:HOSTPORT] or --");
                forwards.push_back(loopback_bridge::parse_forward(argv[++n]));
            }
            for (++n; n < argc; ++n) {
                const std::wstring argument = argv[n];
                if (argument.find(L'"') != std::wstring::npos) throw std::runtime_error("Client arguments may not contain quotes");
                if (!client_arguments.empty()) client_arguments += L' ';
                client_arguments += argument.find(L' ') == std::wstring::npos ? argument : L"\"" + argument + L"\"";
            }
            const bool exact_loopback = client_arguments == L"--BNetServer=127.0.0.1:1119";
            if (!trust_ca_pem.empty() && (private_run_ms == INFINITE || private_run_ms > 180000
                || forwards.size() != 1 || forwards[0].container_port != 1119
                || !exact_loopback))
                throw std::runtime_error("CA probe requires a 1..180-second run, one port-1119 loopback forward and the exact loopback BNetServer argument");
            if (observe_tls && (private_run_ms == INFINITE || private_run_ms > 180000
                || forwards.size() != 1 || forwards[0].container_port != 1119
                || !exact_loopback))
                throw std::runtime_error("TLS observer requires a 1..180-second run, one port-1119 loopback forward and the exact loopback BNetServer argument");
            if (trust_socket_ca && (trust_ca_pem.empty() || !observe_tls))
                throw std::runtime_error("Native socket CA installation requires --trust-ca and --observe-tls");
            if (!lobby_public_modulus.empty() && !trust_socket_ca)
                throw std::runtime_error("Lobby key installation requires bounded loopback --trust-socket-ca diagnostics");
        } catch (const std::exception& error) { std::cerr << error.what() << std::endl; return 2; }
        argc = 3;
    }
    if (argc < 2 || argc > 3) {
        std::cerr << "ow1-offline-launch PATH [--self-test|--graphics-test|--debug|--snapshot|--retail-snapshot|--retail-offline|--wmi-workaround|--run-offline|--map-probe|--map-probe-no-speech|--map-probe-preload|--map-probe-voice-request|--map-probe-stages|--catalogue-schema-probe|--catalogue-import-probe]\n";
        std::cerr << "Final research probes: --retail-map-probe, --retail-map-worker-probe, --retail-map-tick-probe,\n"
                     "  --retail-map-context-probe, --retail-map-context-tick-probe, --retail-map-context-tick-debug, --retail-map-loader-probe, --retail-map-resource-probe, --retail-map-loading-context-probe, --retail-map-metadata-probe\n";
        return 2;
    }
    PSID sid = nullptr;
    const auto profile = L"OW1.Preservation.Offline." + std::to_wstring(GetCurrentProcessId());
    HANDLE job = nullptr;
    HANDLE child_process = nullptr, child_thread = nullptr;
    ScopedAcls original_acls;
    try {
        const auto exe = std::filesystem::absolute(argv[1]).wstring();
        checked(std::filesystem::is_regular_file(exe), "Executable missing");
        const auto mode = argc > 2 ? std::wstring(argv[2]) : L"";
        const bool retail_snapshot = mode == L"--retail-snapshot";
        const bool retail_worker = mode == L"--retail-map-worker-probe";
        const bool retail_tick = mode == L"--retail-map-tick-probe";
        const bool retail_debug = mode == L"--retail-map-context-tick-debug";
        const bool retail_metadata = mode == L"--retail-map-metadata-probe";
        const bool retail_loading_context = mode == L"--retail-map-loading-context-probe" || retail_metadata;
        const bool retail_resources = mode == L"--retail-map-resource-probe" || retail_loading_context;
        const bool retail_loader = mode == L"--retail-map-loader-probe";
        const bool retail_context_tick = mode == L"--retail-map-context-tick-probe" || retail_debug || retail_loader || retail_resources;
        const bool retail_context = mode == L"--retail-map-context-probe" || retail_context_tick;
        const bool retail_map = mode == L"--retail-map-probe" || retail_worker || retail_tick || retail_context;
        const bool retail = retail_snapshot || retail_map || mode == L"--retail-offline" || retail_private;
        const bool disc_interactive = mode == L"--run-offline";
        const bool interactive = disc_interactive || mode == L"--retail-offline" || retail_private;
        const bool import_catalogue = mode == L"--catalogue-import-probe";
        const bool silent_voice = mode == L"--catalogue-schema-probe" || import_catalogue;
        const bool advance_stages = mode == L"--map-probe-stages";
        const bool request_voice = mode == L"--map-probe-voice-request" || advance_stages || silent_voice;
        const bool preload = mode == L"--map-probe-preload" || request_voice;
        const bool omit_speech = mode == L"--map-probe-no-speech" || preload;
        const bool probe_map = mode == L"--map-probe" || omit_speech;
        const bool wmi_workaround = mode == L"--wmi-workaround" || disc_interactive || probe_map;
        if (mode != L"" && mode != L"--self-test" && mode != L"--graphics-test" && mode != L"--debug"
            && mode != L"--snapshot" && mode != L"--wmi-workaround" && !retail && !interactive && !probe_map) throw std::runtime_error("Unknown diagnostic option");
        if (retail && sha256(exe) != retail_profile::sha256)
            throw std::runtime_error("Retail launch only supports the fingerprinted final OW1 executable");
        if ((wmi_workaround || mode == L"--snapshot") && sha256(exe) != disc_profile::sha256)
            throw std::runtime_error("WMI workaround only supports verified Overwatch 1.0.1.27578");
        const HRESULT hr = CreateAppContainerProfile(profile.c_str(), L"OW1 offline test", L"No network capabilities", nullptr, 0, &sid);
        if (FAILED(hr)) throw std::runtime_error("Create profile: " + std::to_string(hr));
        auto client_folder = std::filesystem::path(exe).parent_path().wstring();
        if (retail) {
            const auto executable_folder = std::filesystem::path(exe).parent_path();
            const auto installation = executable_folder.parent_path();
            checked(executable_folder.filename() == L"_retail_"
                && std::filesystem::is_regular_file(installation / L".build.info")
                && std::filesystem::is_directory(installation / L"Data"), "Retail installation layout");
            client_folder = installation.wstring();
            std::cout << "Retail launch uses original files and shared parent CASC storage; no disk patch is applied." << std::endl;
        }
        wchar_t own_path[32768]{};
        checked(GetModuleFileNameW(nullptr, own_path, 32768) != 0, "Launcher path");
        // Capture both before the parent grant can change the launcher's
        // inherited ACL when the executable is inside the client folder.
        original_acls.entries.push_back(std::make_unique<ScopedAcl>(client_folder));
        original_acls.entries.push_back(std::make_unique<ScopedAcl>(own_path));
        original_acls.entries[0]->changed = true;
        allow(sid, client_folder, FILE_GENERIC_READ | FILE_GENERIC_EXECUTE | FILE_GENERIC_WRITE | DELETE,
              SUB_CONTAINERS_AND_OBJECTS_INHERIT);
        original_acls.entries[1]->changed = true;
        allow(sid, own_path, FILE_GENERIC_READ | FILE_GENERIC_EXECUTE, NO_INHERITANCE);
        auto probe = launch(sid, own_path, L"--child-probe");
        ResumeThread(probe.hThread);
        const auto probe_wait = WaitForSingleObject(probe.hProcess, 10000);
        DWORD code = 1;
        if (probe_wait == WAIT_OBJECT_0) GetExitCodeProcess(probe.hProcess, &code);
        else TerminateProcess(probe.hProcess, 1);
        CloseHandle(probe.hThread); CloseHandle(probe.hProcess);
        if (code) throw std::runtime_error("Network isolation probe failed: " + std::to_string(code));
        std::cout << "Network isolation verified; no network capabilities granted." << std::endl;
        if (argc > 2 && std::wstring(argv[2]) == L"--self-test") {
            // No connection is made: exercise cancellation of the host's
            // pending ConnectNamedPipe before its owning object is destroyed.
            { loopback_bridge::HostForwarder bridge(sid, {{1, 1}}); bridge.start(); Sleep(100); }
            std::cout << "Host bridge idle-listener cleanup passed." << std::endl;
            FreeSid(sid); DeleteAppContainerProfile(profile.c_str()); return 0;
        }
        if (argc > 2 && std::wstring(argv[2]) == L"--graphics-test") {
            auto graphics = launch(sid, own_path, L"--graphics-probe");
            ResumeThread(graphics.hThread);
            WaitForSingleObject(graphics.hProcess, 10000);
            TerminateProcess(graphics.hProcess, 0);
            CloseHandle(graphics.hProcess); CloseHandle(graphics.hThread);
            FreeSid(sid); DeleteAppContainerProfile(profile.c_str()); return 0;
        }
        job = CreateJobObjectW(nullptr, nullptr);
        checked(job != nullptr, "Create job");
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits{};
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        checked(SetInformationJobObject(job, JobObjectExtendedLimitInformation, &limits, sizeof(limits)), "Set job cleanup");
        const bool debug = retail_debug || mode == L"--debug";
        std::unique_ptr<loopback_bridge::HostForwarder> forwarder;
        if (retail_private && !forwards.empty()) {
            forwarder = std::make_unique<loopback_bridge::HostForwarder>(sid, forwards);
            forwarder->start();
            std::wstring ports = L"--loopback-bridge " + std::to_wstring(GetCurrentProcessId());
            for (const auto forward : forwards) ports += L" " + std::to_wstring(forward.container_port);
            auto bridge = launch(sid, own_path, ports);
            if (!AssignProcessToJobObject(job, bridge.hProcess)) {
                TerminateProcess(bridge.hProcess, 1); throw std::runtime_error("Assign bridge job failed");
            }
            ResumeThread(bridge.hThread);
            const bool bridge_exited = WaitForSingleObject(bridge.hProcess, 1000) == WAIT_OBJECT_0;
            CloseHandle(bridge.hThread); CloseHandle(bridge.hProcess);
            checked(!bridge_exited, "Container loopback bridge exited during startup");
            std::cout << "Container loopback bridge running; the client still has no network capability." << std::endl;
        }
        if (retail_private) std::wcout << L"Private client arguments: " << client_arguments << std::endl;
        auto child = launch(sid, exe, client_arguments, debug, retail ? client_folder : L"");
        child_process = child.hProcess; child_thread = child.hThread;
        if (!AssignProcessToJobObject(job, child.hProcess)) {
            TerminateProcess(child.hProcess, 1); throw std::runtime_error("Assign child job failed");
        }
        ResumeThread(child.hThread);
        std::cout << "Offline client PID=" << child.dwProcessId << std::endl;
        if (retail_private) {
            PROCESS_BASIC_INFORMATION basic{};
            using Query = NTSTATUS(NTAPI*)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);
            const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
            checked(query && query(child.hProcess, ProcessBasicInformation, &basic, sizeof(basic), nullptr) >= 0, "Private intro image lookup");
            const auto image = read_child<uint64_t>(child.hProcess, reinterpret_cast<uint64_t>(basic.PebBaseAddress) + 0x10);
            retail_world_probe::skip_intro(child.hProcess, image);
        }
        std::unique_ptr<std::jthread> tls_patch_thread;
        if (retail_private && (observe_tls || !trust_ca_pem.empty() || !GetEnvironmentVariableW(L"OW1_SKIP_TLS_PATCH", nullptr, 0))) {
            // Run the chosen exact-build TLS diagnostic while the client starts.
            // The optional CA path calls the original certificate-store API;
            // the legacy path still attempts the guarded in-memory code patch.
            const HANDLE patch_process = child.hProcess;
            const auto primary_tid = child.dwThreadId;
            tls_patch_thread = std::make_unique<std::jthread>([patch_process, primary_tid, trust_ca_pem, observe_tls, trust_socket_ca, lobby_public_modulus](std::stop_token stop) {
                PROCESS_BASIC_INFORMATION basic{};
                using Query = NTSTATUS(NTAPI*)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);
                const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
                if (!query || query(patch_process, ProcessBasicInformation, &basic, sizeof(basic), nullptr) < 0) {
                    std::cout << "bgs TLS patch: image lookup failed; client left unpatched." << std::endl; return;
                }
                uint64_t image = 0;
                if (!ReadProcessMemory(patch_process, reinterpret_cast<char*>(basic.PebBaseAddress) + 0x10, &image, sizeof(image), nullptr) || !image) {
                    std::cout << "bgs TLS patch: image base unavailable; client left unpatched." << std::endl; return;
                }
                try {
                    if (!trust_ca_pem.empty()) retail_ca_probe::run(patch_process, image, primary_tid, trust_ca_pem, stop);
                    if (observe_tls) retail_tls_observer::run(patch_process, image, stop, primary_tid, trust_socket_ca ? trust_ca_pem : std::string{}, lobby_public_modulus);
                    else if (trust_ca_pem.empty()) retail_tls_patch::apply(patch_process, image, stop);
                } catch (const std::exception& error) { std::cout << "Private TLS diagnostic: " << error.what() << std::endl; }
            });
        }
        if (retail_map && !retail_debug) {
            PROCESS_BASIC_INFORMATION basic{};
            using Query = NTSTATUS(NTAPI*)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);
            const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
            checked(query && query(child.hProcess, ProcessBasicInformation, &basic, sizeof(basic), nullptr) >= 0, "Final intro image lookup");
            const auto image = read_child<uint64_t>(child.hProcess, reinterpret_cast<uint64_t>(basic.PebBaseAddress) + 0x10);
            retail_world_probe::skip_intro(child.hProcess, image);
        }
        if (wmi_workaround || (argc > 2 && std::wstring(argv[2]) == L"--snapshot")) {
            PROCESS_BASIC_INFORMATION basic{};
            using Query = NTSTATUS(NTAPI*)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);
            const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
            DWORD64 image = 0;
            if (query && query(child.hProcess, ProcessBasicInformation, &basic, sizeof(basic), nullptr) >= 0) {
                ReadProcessMemory(child.hProcess, reinterpret_cast<char*>(basic.PebBaseAddress) + 0x10, &image, sizeof(image), nullptr);
                unsigned char page[4096]{};
                unsigned char original[4096]{};
                bool have_original = false;
                const auto poll_start = GetTickCount64();
                for (int attempt = 0; GetTickCount64() - poll_start < 10000; ++attempt) {
                    if (ReadProcessMemory(child.hProcess, reinterpret_cast<void*>(image + 0x415000), page, sizeof(page), nullptr)) {
                        if (!have_original) { memcpy(original, page, sizeof(page)); have_original = true; }
                        const unsigned char expected_start[] = {0x48,0x8b,0x4c,0x24,0x70,0x48,0x8d,0x54};
                        if (wmi_workaround ? memcmp(page + 0xeae, expected_start, sizeof(expected_start)) != 0
                                           : !memcmp(original + 0xea0, page + 0xea0, 96)) {
                            if (attempt % 1000 == 0 && WaitForSingleObject(child.hProcess, 0) == WAIT_OBJECT_0) break;
                            continue;
                        }
                        if (wmi_workaround) {
                            const unsigned char expected[] = {0x48,0x8b,0x4c,0x24,0x70,0x48,0x8d,0x54,0x24,0x60,0x45,0x33,0xc9,0x48,0x8b,0x01};
                            checked(!memcmp(page + 0xeae, expected, sizeof(expected)), "Build-specific WMI bytes disagree");
                            // Early WMI failure: return false using this verified function's
                            // prologue layout. Its original cleanup also dereferences null.
                            const unsigned char epilogue[] = {
                                0x48,0x8b,0x9c,0x24,0xa0,0x09,0,0,
                                0x48,0x8b,0xb4,0x24,0xa8,0x09,0,0,
                                0x4c,0x8b,0xb4,0x24,0xb0,0x09,0,0,
                                0x31,0xc0,0x48,0x81,0xc4,0x78,0x09,0,0,
                                0x41,0x5d,0x41,0x5c,0x5f,0x5d,0xc3};
                            void* fallback = nullptr;
                            for (DWORD64 delta = 0x2000000; delta < 0x20000000 && !fallback; delta += 0x10000)
                                fallback = VirtualAllocEx(child.hProcess, reinterpret_cast<void*>(image + delta), 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
                            checked(fallback != nullptr, "Allocate isolated WMI fallback");
                            checked(WriteProcessMemory(child.hProcess, fallback, epilogue, sizeof(epilogue), nullptr), "Write WMI fallback");
                            DWORD executable_protection = 0;
                            checked(VirtualProtectEx(child.hProcess, fallback, 4096, PAGE_EXECUTE_READ, &executable_protection), "WMI fallback protection");
                            const auto displacement = static_cast<int32_t>(reinterpret_cast<DWORD64>(fallback) - (image + 0x415eae + 5));
                            unsigned char patch[] = {0xe9,0,0,0,0};
                            memcpy(patch + 1, &displacement, sizeof(displacement));
                            DWORD old_protection = 0;
                            // Pause the startup thread while replacing its instruction bytes.
                            checked(SuspendThread(child.hThread) != static_cast<DWORD>(-1), "Pause startup thread");
                            CONTEXT startup_context{}; startup_context.ContextFlags = CONTEXT_CONTROL;
                            checked(GetThreadContext(child.hThread, &startup_context), "Read startup instruction pointer");
                            checked(startup_context.Rip < image + 0x415eae || startup_context.Rip >= image + 0x415eb3,
                                    "Startup thread is executing the patch site; retry diagnostic run");
                            unsigned char current[sizeof(expected)]{};
                            checked(ReadProcessMemory(child.hProcess, reinterpret_cast<void*>(image + 0x415eae), current, sizeof(current), nullptr)
                                    && !memcmp(current, expected, sizeof(expected)), "WMI bytes changed before patch");
                            checked(VirtualProtectEx(child.hProcess, reinterpret_cast<void*>(image + 0x415eae), sizeof(patch), PAGE_EXECUTE_READWRITE, &old_protection), "WMI page protection");
                            checked(WriteProcessMemory(child.hProcess, reinterpret_cast<void*>(image + 0x415eae), patch, sizeof(patch), nullptr), "WMI isolated fallback");
                            VirtualProtectEx(child.hProcess, reinterpret_cast<void*>(image + 0x415eae), sizeof(patch), old_protection, &old_protection);
                            FlushInstructionCache(child.hProcess, reinterpret_cast<void*>(image + 0x415eae), sizeof(patch));
                            checked(ResumeThread(child.hThread) != static_cast<DWORD>(-1), "Resume startup thread");
                            std::cout << "Applied in-memory WMI fallback for isolated startup; disk executable unchanged." << std::endl;
                        }
                        if (!wmi_workaround) {
                            const auto path = std::filesystem::path(exe).parent_path() / (L"fault-page-" + std::to_wstring(child.dwProcessId) + L".bin");
                            HANDLE file = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
                            if (file != INVALID_HANDLE_VALUE) {
                                DWORD written = 0; WriteFile(file, page, sizeof(page), &written, nullptr); CloseHandle(file);
                                std::cout << "Captured RVA 0x415000 image base=0x" << std::hex << image << std::dec << std::endl;
                            }
                            HMODULE modules[256]{}; DWORD needed = 0;
                            if (EnumProcessModules(child.hProcess, modules, sizeof(modules), &needed)) {
                                for (DWORD n = 0; n < needed / sizeof(HMODULE) && n < 256; ++n) {
                                    wchar_t name[MAX_PATH]{};
                                    if (GetModuleFileNameExW(child.hProcess, modules[n], name, MAX_PATH))
                                        std::wcout << L"Module 0x" << std::hex << reinterpret_cast<DWORD64>(modules[n]) << L" " << name << std::endl;
                                }
                            }
                            DWORD64 function = 0;
                            ReadProcessMemory(child.hProcess, reinterpret_cast<void*>(image + 0x10ead18), &function, sizeof(function), nullptr);
                            std::cout << "Call preceding fault IAT target=0x" << std::hex << function << std::endl;
                        }
                        break;
                    }
                    if (attempt % 1000 == 0 && WaitForSingleObject(child.hProcess, 0) == WAIT_OBJECT_0) break;
                }
            }
        }
        CloseHandle(child.hThread); child_thread = nullptr;
        bool retail_debug_finished = false;
        if (retail_map) {
            auto retail_probe = [&]() {
            if (WaitForSingleObject(child.hProcess, 20000) != WAIT_TIMEOUT)
                throw std::runtime_error("Final client exited before native map probe");
            PROCESS_BASIC_INFORMATION basic{};
            using Query = NTSTATUS(NTAPI*)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);
            const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
            checked(query && query(child.hProcess, ProcessBasicInformation, &basic, sizeof(basic), nullptr) >= 0, "Final image lookup");
            const auto image = read_child<uint64_t>(child.hProcess, reinterpret_cast<uint64_t>(basic.PebBaseAddress) + 0x10);
            retail_world_probe::run(child.hProcess, image, child.dwThreadId, retail_worker, retail_tick, retail_context, retail_context_tick, retail_loader, retail_resources, retail_loading_context, retail_metadata);
            };
            if (retail_debug) {
                std::atomic<bool> completed{false}; std::exception_ptr probe_error;
                std::jthread probe([&]() {
                    try { retail_probe(); } catch (...) { probe_error = std::current_exception(); }
                    completed = true;
                });
                code = debug_run(child, std::filesystem::path(exe).parent_path(), &completed);
                probe.join(); retail_debug_finished = true;
                std::cout << "Final debug client exited: 0x" << std::hex << code << std::dec << std::endl;
                if (probe_error) std::rethrow_exception(probe_error);
            } else retail_probe();
        }
        if (probe_map) {
            if (WaitForSingleObject(child.hProcess, 20000) != WAIT_TIMEOUT)
                throw std::runtime_error("Disc client exited before map probe");
            PROCESS_BASIC_INFORMATION basic{};
            using Query = NTSTATUS(NTAPI*)(HANDLE, PROCESSINFOCLASS, PVOID, ULONG, PULONG);
            const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
            checked(query && query(child.hProcess, ProcessBasicInformation, &basic, sizeof(basic), nullptr) >= 0, "Disc image lookup");
            const auto image = read_child<uint64_t>(child.hProcess, reinterpret_cast<uint64_t>(basic.PebBaseAddress) + 0x10);
            if (map_probe(child.hProcess, image, omit_speech, preload, request_voice, advance_stages, silent_voice, import_catalogue)) {
                std::cout << "Ending schema-only diagnostic; original resource and gameplay remain unavailable." << std::endl;
                checked(TerminateJobObject(job, 0), "End schema diagnostic job");
                checked(WaitForSingleObject(child.hProcess, 5000) == WAIT_OBJECT_0, "Schema diagnostic cleanup deadline");
            }
        }
        if (debug && !retail_debug_finished) {
            code = debug_run(child, std::filesystem::path(exe).parent_path());
            std::cout << "Debug client exited: 0x" << std::hex << code << std::endl;
        }
        if (interactive) std::cout << (private_run_ms == INFINITE
            ? "Offline window stays open until you exit the client; authentication and gameplay are unavailable."
            : "Private diagnostic is bounded; main-menu access and gameplay remain unverified.") << std::endl;
        const auto wait = debug ? WAIT_OBJECT_0 : WaitForSingleObject(child.hProcess, interactive ? private_run_ms : (probe_map || retail_map) ? 0 : 60000);
        if (wait == WAIT_OBJECT_0) {
            GetExitCodeProcess(child.hProcess, &code);
            std::cout << "Client exited: 0x" << std::hex << code << std::endl;
        } else {
            const auto dump_path = std::filesystem::path(exe).parent_path()
                / ((probe_map || retail_map || retail_private) ? mode.substr(2) + L".dmp" : std::wstring(L"startup-wait.dmp"));
            HANDLE dump = CreateFileW(dump_path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
            if (dump != INVALID_HANDLE_VALUE) {
                MiniDumpWriteDump(child.hProcess, child.dwProcessId, dump,
                    static_cast<MINIDUMP_TYPE>(MiniDumpWithThreadInfo | MiniDumpWithFullMemory), nullptr, nullptr, nullptr);
                CloseHandle(dump);
            }
            std::cout << "Owned client still alive; ending bounded diagnostic run." << std::endl;
            TerminateJobObject(job, 3); WaitForSingleObject(child.hProcess, 5000); code = 3;
        }
        // Stop/join while the owned process handle is still valid. Exceptions
        // also request stop through jthread destruction before catch cleanup.
        if (tls_patch_thread) { tls_patch_thread->request_stop(); tls_patch_thread->join(); }
        CloseHandle(child.hProcess); child_process = nullptr;
        CloseHandle(job); job = nullptr;
        FreeSid(sid); sid = nullptr; DeleteAppContainerProfile(profile.c_str());
        return code ? 1 : 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << std::endl;
        if (child_process && argc > 2 && std::wstring(argv[2]).starts_with(L"--retail-map-")) {
            DWORD exit_code = 0; GetExitCodeProcess(child_process, &exit_code);
            std::cerr << "Owned final diagnostic process status=0x" << std::hex << exit_code << std::dec << std::endl;
            if (exit_code == STILL_ACTIVE) {
                const auto path = std::filesystem::absolute(argv[1]).parent_path() / L"retail-map-probe-error.dmp";
                HANDLE dump = CreateFileW(path.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
                if (dump != INVALID_HANDLE_VALUE) {
                    const bool saved = MiniDumpWriteDump(child_process, GetProcessId(child_process), dump,
                        static_cast<MINIDUMP_TYPE>(MiniDumpWithThreadInfo | MiniDumpWithFullMemory), nullptr, nullptr, nullptr);
                    CloseHandle(dump);
                    std::cerr << "Final failure snapshot saved=" << saved << std::endl;
                }
            }
        }
        if (job) CloseHandle(job);
        if (child_process) { TerminateProcess(child_process, 1); WaitForSingleObject(child_process, 5000); CloseHandle(child_process); }
        if (child_thread) CloseHandle(child_thread);
        if (sid) { FreeSid(sid); DeleteAppContainerProfile(profile.c_str()); }
        return 1;
    }
}
