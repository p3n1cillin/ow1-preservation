#pragma once

// Opt-in control for an owned, bounded private session. Wait for a native
// Practice request, then ask the original loader for its header once. The
// callback neither submits a world request nor ticks/changes a world state.
namespace retail_private_preload {
bool pending_practice(HANDLE process, uint64_t image, std::stop_token stop) {
    const auto mask = read_child<uint64_t>(process, image + retail_world_probe::owner_operand)
        ^ retail_world_probe::owner_constant;
    uint64_t cursor = 0, scanned = 0;
    const auto deadline = GetTickCount64() + 3000;
    MEMORY_BASIC_INFORMATION region{};
    while (!stop.stop_requested() && GetTickCount64() < deadline
           && VirtualQueryEx(process, reinterpret_cast<void*>(cursor), &region, sizeof(region))) {
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress);
        const auto size = static_cast<uint64_t>(region.RegionSize);
        if (!size || start + size <= cursor) break;
        cursor = start + size;
        if (region.State != MEM_COMMIT || region.Type != MEM_PRIVATE
            || (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            || !(region.Protect & (PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY))) continue;
        for (uint64_t offset = 0; offset < size; offset += 1024 * 1024) {
            if (stop.stop_requested() || GetTickCount64() >= deadline) return false;
            const auto bytes = static_cast<SIZE_T>(std::min<uint64_t>(size - offset, 1024 * 1024 + 7));
            scanned += bytes;
            if (scanned > 4ULL * 1024 * 1024 * 1024) return false;
            std::vector<unsigned char> block(bytes); SIZE_T count = 0;
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(start + offset), block.data(), bytes, &count)
                || count != bytes) continue;
            for (size_t at = 0; at + 8 <= bytes && at < 1024 * 1024; at += 8) {
                uint64_t value = 0; memcpy(&value, block.data() + at, 8);
                if (value != image + retail_world_probe::vtable) continue;
                const auto world = start + offset + at;
                try {
                    if (read_child<uint64_t>(process, world + 0x10) != image + retail_world_probe::secondary
                        || read_child<unsigned char>(process, world + 0x18) != 2) continue;
                    const auto owner = read_child<uint64_t>(process, world + 8) ^ mask;
                    if (!owner || owner >= 0x800000000000 || owner % 8
                        || read_child<uint64_t>(process, owner) != image + retail_world_probe::owner_vtable) continue;
                    const auto request = read_child<uint64_t>(process, world + 0x20);
                    if (!request || request >= 0x800000000000 || request % 8) continue;
                    // The header's +0x50 reference names the typed Practice map
                    // variant. Permit it and the canonical Practice map to
                    // isolate the variant flag from the map's resource type.
                    const auto map = read_child<uint64_t>(process, request);
                    // Both authored Practice modes use this map header. Mode
                    // 0x18 selects the Practice-specific team controller; 0x5a
                    // is the existing diagnostic baseline.
                    const auto mode = read_child<uint64_t>(process, request + 8);
                    if ((map == 0x0790000000000688ULL || map == 0x0800000000000688ULL
                         || map == 0x0800010000000688ULL)
                        && (mode == 0x0230000000000018ULL || mode == 0x023000000000005aULL)) return true;
                } catch (const std::exception&) { /* A changing live object is not a valid match. */ }
            }
        }
    }
    return false;
}

void run(HANDLE process, uint64_t image, DWORD primary_thread, std::stop_token stop) {
    using retail_world_probe::guard;
    std::cout << "Practice preload control armed; waiting for original pending request." << std::endl;
    while (!stop.stop_requested() && WaitForSingleObject(process, 250) == WAIT_TIMEOUT) {
        if (pending_practice(process, image, stop)) break;
    }
    if (stop.stop_requested() || WaitForSingleObject(process, 0) != WAIT_TIMEOUT) return;
    // Reuse the instruction/profile guards of the existing standalone control.
    guard(process, image, 0x171e8e0, {0x4c,0x8b,0xdc,0x49,0x89,0x5b,0x18,0x57,0x48,0x81,0xec,0x80,0,0,0});
    guard(process, image, 0x171e926, {0x49,0x89,0x4b,0x98});
    guard(process, image, 0x171e936, {0x89,0x54,0x24,0x30,0xe8,0x61,0xe3,0xff,0xff});
    guard(process, image, 0x171b220, {0x33,0xd2,0xc7,0x41,0x10,4,0,0,0});
    const auto remote = reinterpret_cast<uint64_t>(VirtualAllocEx(process, nullptr, 65536, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    if (!remote) throw std::runtime_error("Private preload callback allocation failed");
    constexpr DWORD code_offset = 256, unwind_offset = 128, table_offset = 160;
    unsigned char page[4096]{};
    // ALLOC_SMALL unwind record for the callback's 40-byte native stack frame.
    const unsigned char unwind[] = {1,4,1,0,4,0x42,0,0};
    memcpy(page + unwind_offset, unwind, sizeof(unwind));
    std::vector<unsigned char> code;
    auto emit = [&](std::initializer_list<unsigned char> bytes) { code.insert(code.end(), bytes); };
    auto value = [&](auto item) { const auto p = reinterpret_cast<const unsigned char*>(&item); code.insert(code.end(), p, p + sizeof(item)); };
    emit({0x48,0x83,0xec,0x28,0x48,0xb8}); value(remote);
    emit({0xc7,0x40,0x60,1,0,0,0,0xc7,0,1,0,0,0});
    emit({0x48,0xb9}); value(remote + table_offset); emit({0xba,1,0,0,0,0x49,0xb8}); value(remote);
    emit({0x48,0xb8}); value(child_function_table_api(process)); emit({0xff,0xd0,0x48,0xb9}); value(remote);
    emit({0x88,0x41,8,0xc7,0x01,3,0,0,0,0x84,0xc0,0x0f,0x84});
    const auto registration_failed = code.size(); value(int32_t{0});
    emit({0x48,0xb9}); value(uint64_t{0x0790000000000688}); emit({0xba,4,0,0,0,0x48,0xb8}); value(image + 0x171e8e0);
    emit({0xff,0xd0,0x48,0xb9}); value(remote); emit({0x48,0x89,0x41,0x20,0xc7,0x01,2,0,0,0});
    const auto relative = static_cast<int32_t>(code.size() - registration_failed - 4);
    memcpy(code.data() + registration_failed, &relative, 4);
    emit({0x48,0x83,0xc4,0x28,0x48,0xb8}); value(remote); emit({0xc7,0x40,0x60,0,0,0,0,0x48,0xb9}); value(remote + 4096);
    emit({0x33,0xd2,0x48,0xb8}); value(child_function_table_api(process, "NtContinue")); emit({0xff,0xe0});
    if (code_offset + code.size() >= sizeof(page)) throw std::runtime_error("Private preload callback code bound");
    memcpy(page + code_offset, code.data(), code.size());
    const RUNTIME_FUNCTION entry{code_offset, static_cast<DWORD>(code_offset + code.size()), unwind_offset};
    memcpy(page + table_offset, &entry, sizeof(entry));
    SIZE_T count = 0; DWORD previous = 0;
    if (!WriteProcessMemory(process, reinterpret_cast<void*>(remote), page, sizeof(page), &count) || count != sizeof(page)
        || !VirtualProtectEx(process, reinterpret_cast<void*>(remote), sizeof(page), PAGE_EXECUTE_READWRITE, &previous)
        || !FlushInstructionCache(process, reinterpret_cast<void*>(remote + code_offset), code.size()))
        throw std::runtime_error("Private preload callback preparation failed");
    retail_world_probe::PrimarySubmission submission(process, primary_thread, remote, true);
    bool scheduled = false;
    while (!stop.stop_requested() && WaitForSingleObject(process, 10) == WAIT_TIMEOUT) {
        if (!scheduled) scheduled = submission.schedule(0, remote + code_offset);
        if (read_child<uint32_t>(process, remote + 96) || !read_child<uint32_t>(process, remote)) continue;
        std::cout << "Practice preload control returned: scheduled=" << scheduled
                  << ", unwind_registered=" << bool(read_child<unsigned char>(process, remote + 8))
                  << ", native_api_called=" << (read_child<uint32_t>(process, remote) == 2)
                  << ", resource_reference_present=" << bool(read_child<uint64_t>(process, remote + 32)) << std::endl;
        return; // Native reference and callback table live only until owned job exit.
    }
}
} // namespace retail_private_preload
