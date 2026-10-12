#pragma once

// Final 104319 only. The idle handler dereferences a 0x150-byte map request;
// its native API copies that request into a native-owned allocation. The probe
// changes only the map index in an independently copied native default request.
// State transitions, resource readiness and callbacks remain native.
namespace retail_world_probe {
constexpr uint64_t vtable = 0x2655d88, secondary = 0x2618220, owner_vtable = 0x260be40;
constexpr uint64_t owner_operand = 0x2ee48a1, owner_constant = 0x4dfd564467c27b96;
constexpr uint64_t tick = 0xb4b5f0, request_api = 0xb4b1c0, defaults = 0x2d1a8c0;

void guard(HANDLE process, uint64_t image, uint64_t rva, std::initializer_list<unsigned char> expected) {
    std::vector<unsigned char> actual(expected.size()); SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + rva), actual.data(), actual.size(), &count)
        || count != actual.size() || !std::equal(actual.begin(), actual.end(), expected.begin()))
        throw std::runtime_error("Final world instruction guard differs");
}

uint64_t find_world(HANDLE process, uint64_t image) {
    const auto operand = read_child<uint64_t>(process, image + owner_operand);
    uint64_t found = 0, cursor = 0, scanned = 0;
    const auto deadline = GetTickCount64() + 15000;
    MEMORY_BASIC_INFORMATION region{};
    while (VirtualQueryEx(process, reinterpret_cast<void*>(cursor), &region, sizeof(region))) {
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress), size = static_cast<uint64_t>(region.RegionSize);
        if (!size || start + size <= cursor) break;
        cursor = start + size;
        if (GetTickCount64() > deadline) throw std::runtime_error("Final world search deadline");
        if (region.State != MEM_COMMIT || region.Type != MEM_PRIVATE
            || (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            || !(region.Protect & (PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY))) continue;
        for (uint64_t offset = 0; offset < size; offset += 1024 * 1024) {
            const auto bytes = static_cast<SIZE_T>(std::min<uint64_t>(size - offset, 1024 * 1024 + 7));
            scanned += bytes;
            if (scanned > 4ULL * 1024 * 1024 * 1024) throw std::runtime_error("Final world search budget");
            std::vector<unsigned char> block(bytes); SIZE_T read = 0;
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(start + offset), block.data(), bytes, &read) || read != bytes) continue;
            for (size_t at = 0; at + 8 <= bytes && at < 1024 * 1024; at += 8) {
                uint64_t value = 0; memcpy(&value, block.data() + at, 8);
                if (value != image + vtable) continue;
                const auto address = start + offset + at;
                if (read_child<uint64_t>(process, address + 16) != image + secondary) continue;
                const auto owner = read_child<uint64_t>(process, address + 8) ^ operand ^ owner_constant;
                if (!owner || owner >= 0x800000000000 || owner % 8
                    || read_child<uint64_t>(process, owner) != image + owner_vtable) continue;
                if (found && found != address) throw std::runtime_error("Ambiguous final world object");
                found = address;
            }
        }
    }
    return found;
}

void skip_intro(HANDLE process, uint64_t image) {
    // The native ShowIntro registration initializes this word to 0x01000101;
    // its normal dismissal writes the low byte to zero. Set only that option
    // after its own initializer, before the startup renderer checks it.
    const auto deadline = GetTickCount64() + 30000;
    while (GetTickCount64() < deadline) {
        if (WaitForSingleObject(process, 10) != WAIT_TIMEOUT)
            throw std::runtime_error("Final client exited before intro option initialization");
        uint64_t identity = 0; SIZE_T count = 0;
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + 0x2f54210), &identity, sizeof(identity), &count)
            || count != sizeof(identity) || identity != image + 0x260bf68) continue;
        const auto value = read_child<uint32_t>(process, image + 0x2f54248);
        if (value != 0x01000101 && value != 0x01000100) continue;
        guard(process, image, 0x138576, {0xc7,0x05,0xc8,0xbc,0xe1,0x02,0x01,0x01,0x00,0x01});
        guard(process, image, 0x59a5d5, {0x80,0x3d,0x6c,0x9c,0x9b,0x02,0x00});
        const unsigned char disabled = 0;
        if (!WriteProcessMemory(process, reinterpret_cast<void*>(image + 0x2f54248), &disabled, 1, &count) || count != 1)
            throw std::runtime_error("Final native intro option write failed");
        std::cout << "Native ShowIntro option disabled for this owned diagnostic process." << std::endl;
        return;
    }
    throw std::runtime_error("Final native intro option initialization deadline");
}

struct PrimarySubmission {
    HANDLE process;
    uint64_t remote, delay;
    bool native_stack;
    std::unique_ptr<void, decltype(&CloseHandle)> thread;
    PrimarySubmission(HANDLE child, DWORD tid, uint64_t allocation, bool use_native_stack)
        : process(child), remote(allocation), delay(child_function_table_api(child, "NtDelayExecution")), native_stack(use_native_stack),
          thread(OpenThread(THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT | THREAD_SET_CONTEXT | THREAD_QUERY_INFORMATION,
                            FALSE, tid), CloseHandle) {
        if (!thread || GetProcessIdOfThread(thread.get()) != GetProcessId(process))
            throw std::runtime_error("Final context thread identity differs");
        if (read_child<unsigned char>(process, delay + 20) != 0xc3)
            throw std::runtime_error("Native delay return guard differs");
    }
    bool schedule(uint64_t world, uint64_t callback) {
        if (read_child<uint32_t>(process, remote + 96)) return false;
        const auto suspended = SuspendThread(thread.get());
        if (suspended == DWORD(-1)) throw std::runtime_error("Final context suspension failed");
        try {
            if (suspended) throw std::runtime_error("Final context thread already suspended");
            CONTEXT original{}; original.ContextFlags = CONTEXT_ALL;
            if (!GetThreadContext(thread.get(), &original)) throw std::runtime_error("Final context read failed");
            bool redirected = false;
            // Do not overwrite the saved context while an earlier callback is
            // still running (including a native wait on the scratch stack).
            if (original.Rip == delay + 20 && !(original.Rsp >= remote && original.Rsp < remote + 65536)
                && !read_child<uint32_t>(process, remote + 96)) {
                auto stack = remote + 65536 - 40;
                if (native_stack) {
                    if (original.Rsp < 8192 || (original.Rsp & 15) != 8)
                        throw std::runtime_error("Final original stack alignment differs");
                    stack = original.Rsp - 4096;
                    MEMORY_BASIC_INFORMATION memory{};
                    if (!VirtualQueryEx(process, reinterpret_cast<void*>(stack - 256), &memory, sizeof(memory))
                        || memory.State != MEM_COMMIT || memory.Type != MEM_PRIVATE
                        || (memory.Protect & (PAGE_GUARD | PAGE_NOACCESS))
                        || !(memory.Protect & (PAGE_READWRITE | PAGE_WRITECOPY))
                        || stack >= reinterpret_cast<uint64_t>(memory.BaseAddress) + memory.RegionSize)
                        throw std::runtime_error("Final original stack workspace unavailable");
                }
                SIZE_T count = 0;
                if (!WriteProcessMemory(process, reinterpret_cast<void*>(remote + 4096), &original, sizeof(original), &count)
                    || count != sizeof(original)) throw std::runtime_error("Final saved context write failed");
                auto context = original; context.Rip = callback; context.Rsp = stack; context.Rcx = world;
                if (!SetThreadContext(thread.get(), &context))
                    throw std::runtime_error("Final context redirect failed: " + std::to_string(GetLastError()));
                redirected = true;
            }
            if (ResumeThread(thread.get()) == DWORD(-1)) throw std::runtime_error("Final context resume failed");
            return redirected;
        } catch (...) { ResumeThread(thread.get()); throw; }
    }
};

uint64_t find_context_service(HANDLE process, uint64_t image, uint64_t context) {
    const auto root = read_child<uint64_t>(process, image + 0x2f586e0);
    const auto operand = read_child<uint64_t>(process, image + 0x2ee4bd0);
    if (!root || root >= 0x800000000000 || root % 8) throw std::runtime_error("Final context root bounds");
    const auto array = read_child<uint64_t>(process, root + 0x140) ^ (0x4e3494c633194824ULL - operand);
    if (!array || array >= 0x800000000000 || array % 8) throw std::runtime_error("Final context array bounds");
    uint64_t slots[256]{}, found = 0; SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(array), slots, sizeof(slots), &count) || count != sizeof(slots))
        throw std::runtime_error("Final context component slots unavailable");
    for (auto address : slots) {
        if (!address || address >= 0x800000000000 || address % 8) continue;
        uint64_t blob[0x1a8 / 8]{};
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(address), blob, sizeof(blob), &count) || count != sizeof(blob)) continue;
        if (blob[0] != image + 0x2611278 || (blob[1] ^ 0xf3b530a5300e4c1aULL) != root
            || blob[0x1a0 / 8] != context) continue;
        if (found && found != address) throw std::runtime_error("Ambiguous final context service");
        found = address;
    }
    if (!found) throw std::runtime_error("Final current context service unavailable");
    return found;
}

void run(HANDLE process, uint64_t image, DWORD primary_thread, bool worker_probe, bool tick_probe, bool context_probe, bool context_tick, bool loader_probe, bool resource_probe, bool loading_context_probe, bool metadata_probe) {
    guard(process, image, 0xb4a5c2, {0x48,0x8d,0x05,0xbf,0xb7,0xb0,0x01,0x48,0x89,0x03});
    guard(process, image, 0xb4b5cd, {0xc6,0x41,0x18,0x02});
    guard(process, image, 0xb52b88, {0x48,0x8b,0x79,0x20,0x48,0x85,0xff});
    guard(process, image, 0xb52bc3, {0x8b,0x07});
    guard(process, image, 0xb4b1de, {0x80,0x79,0x18,0x02,0x48,0x8b,0xfa,0x48,0x8b,0xd9});
    guard(process, image, 0xb4b226, {0xb9,0x50,0x01,0,0});
    guard(process, image, 0xb4b3c7, {0x48,0x8b,0x73,0x20,0x48,0x89,0x7b,0x20});
    if (loader_probe || resource_probe) {
        guard(process, image, 0x171b800, {0x48,0x83,0xec,0x38});
        guard(process, image, 0x171b815, {0xe8,0x06,0x00,0x00,0x00});
        guard(process, image, 0x171c0b0, {0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x30});
        guard(process, image, 0xb542ef, {0x49,0x8b,0xcc,0xe8,0xb9,0x7d,0xbc,0x00});
        guard(process, image, 0x171b82c, {0x48,0x8b,0x0d,0x05,0x3b,0xb0,0x01});
        guard(process, image, 0x1734310, {0x48,0x89,0x54,0x24,0x10,0x48,0x83,0xec,0x28});
        guard(process, image, 0xb52b20, {0x48,0x89,0x4c,0x24,0x08,0x55,0x57,0x41,0x57});
        guard(process, image, 0xb523f0, {0x48,0x89,0x74,0x24,0x20,0x57,0x48,0x83,0xec,0x20});
        guard(process, image, 0xb4ff60, {0x48,0x89,0x5c,0x24,0x08,0x57,0x48,0x83,0xec,0x20});
        unsigned at = 0;
        for (uint32_t expected : {0xb4ccca,0xb4ccd4,0xb4cce7,0xb4ccf1,0xb4ccfb,0xb4cd05,0xb4cd20,0xb4cd0f}) {
            if (read_child<uint32_t>(process, image + 0xb4d8e4 + at * 4) != expected)
                throw std::runtime_error("Final native loading state table differs");
            ++at;
        }
    }
    const auto slot = image + vtable + 14 * 8;
    if (resource_probe) {
        guard(process, image, 0x171e8e0, {0x4c,0x8b,0xdc,0x49,0x89,0x5b,0x18,0x57,0x48,0x81,0xec,0x80,0,0,0});
        guard(process, image, 0x171e926, {0x49,0x89,0x4b,0x98}); // request GUID
        guard(process, image, 0x171e936, {0x89,0x54,0x24,0x30,0xe8,0x61,0xe3,0xff,0xff}); // priority and native request
        guard(process, image, 0x171b220, {0x33,0xd2,0xc7,0x41,0x10,4,0,0,0}); // native default priority
    }
    if (read_child<uint64_t>(process, slot) != image + tick) throw std::runtime_error("Final world tick slot differs");
    uint64_t world = 0;
    const auto ready_deadline = GetTickCount64() + 300000;
    std::cout << "Waiting for final native world creation (startup cinematics may still be active)." << std::endl;
    while (!(world = find_world(process, image))) {
        if (GetTickCount64() >= ready_deadline) throw std::runtime_error("Final world creation deadline");
        if (WaitForSingleObject(process, 3000) != WAIT_TIMEOUT)
            throw std::runtime_error("Final client exited before world creation");
    }
    std::cout << "Final native world object verified." << std::endl;
    if (read_child<unsigned char>(process, world + 0x18) != 2 || read_child<uint64_t>(process, world + 0x20))
        throw std::runtime_error("Final world is not idle without a request");
    unsigned char original_defaults[0x150]{}; SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + defaults), original_defaults, sizeof(original_defaults), &count)
        || count != sizeof(original_defaults)) throw std::runtime_error("Final native defaults unavailable");
    for (unsigned at = 0; at < 0x38; ++at)
        if (original_defaults[at]) throw std::runtime_error("Final native default scalar fields differ");
    for (auto [offset, capacity] : {std::pair<unsigned,unsigned>{0x38,4}, {0x68,16}, {0xf8,8}}) {
        uint64_t pointer = 0; uint32_t size = 0, cap = 0;
        memcpy(&pointer, original_defaults + offset, 8); memcpy(&size, original_defaults + offset + 8, 4);
        memcpy(&cap, original_defaults + offset + 12, 4);
        if (pointer != image + defaults + offset + 16 || size || cap != (0x80000000 | capacity))
            throw std::runtime_error("Final default inline vector differs");
    }
    if (original_defaults[0x148]) throw std::runtime_error("Final default trailing flag differs");
    if (loading_context_probe) {
        guard(process, image, 0x684610, {0x48,0x89,0x74,0x24,0x10,0x55,0x57,0x41,0x54,0x41,0x56,0x41,0x57});
        guard(process, image, 0x684671, {0x48,0x8d,0x15,0xb8,0xba,0xb9,0x02});
        guard(process, image, 0x684746, {0x48,0x8d,0x05,0x43,0xcb,0xf8,0x01,0x48,0x89,0x01});
        guard(process, image, 0x835ab6, {0xba,2,0,0,0});
        guard(process, image, 0x835ad8, {0xf0,0xff,0x40,0x08});
        guard(process, image, 0x6855a0, {0x48,0x89,0x5c,0x24,0x10,0x48,0x89,0x74,0x24,0x18});
        guard(process, image, 0x6857fc, {0x49,0x8b,0x06,0x48,0x89,0x86,0xa0,1,0,0});
        guard(process, image, 0x6858ca, {0x80,0xbd,0x98,0,0,0,0});
        unsigned char native_empty_context[32]{};
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + 0x3220130), native_empty_context, 32, &count)
            || count != 32 || memcmp(native_empty_context, original_defaults + 0x18, 32))
            throw std::runtime_error("Final native default loading context differs");
    }
    if (metadata_probe) {
        guard(process, image, 0x6855ca, {0x48,0x8b,0x05,0x0f,0x31,0x8d,0x02});
        guard(process, image, 0x6855e3, {0x48,0x2b,0x1d,0xe6,0xf5,0x85,0x02});
        guard(process, image, 0x681870, {0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x74,0x24,0x18});
        guard(process, image, 0x6818ad, {0x80,0xba,0x69,1,0,0,0});
        guard(process, image, 0x682250, {0x48,0x8b,0xc4,0x55,0x41,0x55,0x41,0x56,0x41,0x57});
        guard(process, image, 0x68225e, {0x4c,0x8b,0xba,0x58,1,0,0});
        guard(process, image, 0x1866230, {0x48,0x83,0xec,0x28,0xba,0x10,0,0,0});
        guard(process, image, 0x681909, {0x48,0x8d,0x05,0x30,0x4e,0xfd,0x01});
        guard(process, image, 0x81c1e0, {0x33,0xd2,0x66,0xc7,0x41,0x10,0x0d,0});
        guard(process, image, 0x8217f0, {0x48,0x89,0x5c,0x24,0x10,0x56,0x48,0x83,0xec,0x20});
        guard(process, image, 0x821820, {0x83,0x3d,0xa1,0xd1,0x73,0x02,0});
    }
    const auto remote = reinterpret_cast<uint64_t>(VirtualAllocEx(process, nullptr, context_probe ? 65536 : 4096, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    if (!remote) throw std::runtime_error("Final callback allocation failed");
    constexpr unsigned code_offset = 256, config_offset = 2048, unwind_offset = 128, table_offset = 160;
    constexpr unsigned dispatch_offset = 1032, dispatch_bytes = 512;
    unsigned char page[4096]{};
    page[56] = 0xff; // Native map-header availability has not been queried.
    page[78] = resource_probe ? 2 : 0; // Bounded immediate native updates.
    const uint32_t metadata_version = 0x31505246; memcpy(page + 60, &metadata_version, 4); // FRP1
    if (tick_probe) {
        if (!ReadProcessMemory(process, reinterpret_cast<void*>(image + vtable - 8),
                page + dispatch_offset - 8, dispatch_bytes + 8, &count) || count != dispatch_bytes + 8)
            throw std::runtime_error("Final dispatch copy read failed");
        const auto callback = remote + code_offset;
        memcpy(page + dispatch_offset + 14 * 8, &callback, 8);
    }
    memcpy(page + config_offset, original_defaults, sizeof(original_defaults));
    const uint32_t practice_index = 0x688; memcpy(page + config_offset, &practice_index, 4);
    for (unsigned at : {0x38,0x68,0xf8}) {
        const auto pointer = remote + config_offset + at + 16; memcpy(page + config_offset + at, &pointer, 8);
    }
    // Tick mode submits on the native world thread, then chains the original
    // tick with its arguments intact. Other modes retain the APC/worker probe.
    // No world-ready flags are changed.
    // ALLOC_LARGE unwind record describes the 0xd8-byte stack frame.
    const unsigned char unwind[] = {1,7,2,0,7,1,27,0}; memcpy(page + unwind_offset, unwind, sizeof(unwind));
    std::vector<unsigned char> code;
    auto emit = [&](std::initializer_list<unsigned char> bytes) { code.insert(code.end(), bytes); };
    auto value = [&](auto item) { const auto ptr = reinterpret_cast<const unsigned char*>(&item); code.insert(code.end(), ptr, ptr + sizeof(item)); };
    auto branch = [&]() { emit({0x0f,0x85}); auto at = code.size(); value(int32_t{0}); return at; };
    emit({0x48,0x81,0xec,0xd8,0,0,0});
    emit({0x48,0x89,0x4c,0x24,0x20,0x48,0x89,0x54,0x24,0x28,0x4c,0x89,0x44,0x24,0x30,0x4c,0x89,0x4c,0x24,0x38});
    for (unsigned reg = 0; reg < 4; ++reg) emit({0xf3,0x0f,0x7f,static_cast<unsigned char>(0x44 + reg * 8),0x24,static_cast<unsigned char>(0x40 + reg * 16)});
    emit({0x48,0xb8}); value(remote); emit({0xf0,0xff,0x40,0x04,0x48,0x89,0x48,0x20,0xc7,0x40,0x60,1,0,0,0,0xc6,0x40,0x5e,0});
    // Syscall return may replace RCX with the return PC. Context mode uses the
    // separately verified world pointer rather than a callback argument.
    if (context_probe) { emit({0x48,0xb9}); value(world); }
    emit({0x48,0xb8}); value(world); emit({0x48,0x39,0xc1}); const auto other_world = branch();
    emit({0x48,0xb9}); value(remote); emit({0x33,0xc0,0xba,1,0,0,0,0xf0,0x0f,0xb1,0x11});
    const auto already_done = branch(); // atomic one-shot owns submission
    emit({0x48,0xb9}); value(remote + table_offset); emit({0xba,1,0,0,0,0x49,0xb8}); value(remote);
    emit({0x48,0xb8}); value(child_function_table_api(process)); emit({0xff,0xd0});
    emit({0x48,0xb9}); value(remote + 8); emit({0x88,0x01,0x84,0xc0,0x0f,0x84});
    const auto registration_failed = code.size(); value(int32_t{0});
    if (loading_context_probe) {
        // Follow the original caller: construct type 2 from the native empty
        // key, retain one reference, and pass another to its consuming API.
        // That API publishes the context and dispatches its native change
        // notifications. Native processing owns readiness; this probe supplies
        // no metadata or ready bit.
        emit({0x48,0xb9}); value(remote); emit({0xc6,0x81,0xc0,0,0,0,1});
        emit({0x48,0xb9}); value(remote + 176); emit({0xba,2,0,0,0,0x49,0xb8}); value(remote + config_offset + 0x18);
        emit({0x48,0xb8}); value(image + 0x684610); emit({0xff,0xd0,0x48,0xb9}); value(remote + 176);
        emit({0x48,0x8b,0x01,0x48,0x85,0xc0}); const auto no_context = branch();
        // JZ is required here; the branch helper emits JNZ by default.
        code[no_context - 1] = 0x84;
        emit({0x48,0xba}); value(image + 0x2611290); emit({0x48,0x39,0x10}); const auto wrong_context = branch();
        emit({0x83,0x78,0x10,2}); const auto wrong_type = branch();
        emit({0x48,0x89,0x41,0x08,0xf0,0xff,0x40,0x08,0xc6,0x41,0x13,1});
        emit({0x48,0xb9}); value(remote + 184); emit({0x48,0xb8}); value(image + 0x6855a0); emit({0xff,0xd0,0x48,0xb9}); value(remote);
        emit({0x88,0x81,0xc1,0,0,0,0xc6,0x81,0xc2,0,0,0,1});
        for (auto at : {no_context, wrong_context, wrong_type}) {
            const auto relative = static_cast<int32_t>(code.size() - at - 4); memcpy(code.data() + at, &relative, 4);
        }
    }
    if (metadata_probe) {
        // Retain an independent native kind-13 request so an asynchronous
        // failure remains inspectable after the service drops its reference.
        // Follow its original aligned-allocation/control-block/constructor
        // sequence. No request payload, completion or response is supplied.
        emit({0x48,0xb9}); value(remote + 200); emit({0xc6,0x01,1,0xb9,0x58,1,0,0});
        emit({0x48,0xb8}); value(image + 0x1866230); emit({0xff,0xd0,0x48,0xb9}); value(remote + 240);
        emit({0x48,0x89,0x01,0x48,0x85,0xc0,0x0f,0x84}); const auto no_request = code.size(); value(int32_t{0});
        emit({0x48,0xba}); value(image + 0x2656740); emit({0x48,0x89,0x10,0xc7,0x40,0x08,2,0,0,0,0xc7,0x40,0x0c,1,0,0,0});
        emit({0x48,0x8d,0x48,0x10,0x48,0xb8}); value(image + 0x81c1e0); emit({0xff,0xd0});
        emit({0x48,0xb9}); value(remote + 248); emit({0x48,0x89,0x01,0x48,0xba}); value(remote + 3072);
        emit({0x48,0x89,0x02,0x48,0xb9}); value(remote + 240); emit({0x48,0x8b,0x01,0x48,0x89,0x42,0x08});
        emit({0x48,0xb8}); value(image + 0x2f5e9c8); emit({0x8b,0x00,0x48,0xb9}); value(remote + 224);
        emit({0x89,0x01,0x89,0x41,0x04,0xc7,0x41,0x08,1,0,0,0});
        emit({0x48,0xb9}); value(remote + 3072); emit({0x48,0xb8}); value(image + 0x8217f0); emit({0xff,0xd0,0x48,0xb9}); value(remote + 201);
        emit({0xc6,0x01,1,0x88,0x41,0x01});
        const auto relative = static_cast<int32_t>(code.size() - no_request - 4); memcpy(code.data() + no_request, &relative, 4);
    }
    emit({0x48,0xb9}); value(world); emit({0x48,0xba}); value(remote + config_offset);
    emit({0x48,0xb8}); value(image + request_api); emit({0xff,0xd0});
    emit({0x48,0xb9}); value(world); emit({0x48,0x8b,0x41,0x20});
    emit({0x48,0xb9}); value(remote + 16); emit({0x48,0x89,0x01,0x48,0x85,0xc0,0x0f,0x84});
    const auto no_descriptor = code.size(); value(int32_t{0});
    emit({0x8b,0x00,0x89,0x41,0x08});
    const auto mark_done = code.size();
    const auto no_descriptor_relative = static_cast<int32_t>(mark_done - no_descriptor - 4);
    memcpy(code.data() + no_descriptor, &no_descriptor_relative, 4);
    emit({0x48,0xb9}); value(remote); emit({0xc7,0x01,2,0,0,0});
    if (resource_probe) {
        // Submit once through the native resource API with its normal default
        // priority. The returned native reference stays alive until job exit.
        // No resource data or completion state is supplied by this project.
        emit({0x48,0xb9}); value(uint64_t{0x0790000000000688}); emit({0xba,4,0,0,0});
        emit({0x48,0xb8}); value(image + 0x171e8e0); emit({0xff,0xd0,0x48,0xb9}); value(remote);
        emit({0x48,0x89,0x41,0x40,0xc6,0x41,0x48,1});
    }
    const auto pump = code.size();
    if (metadata_probe) {
        // The verified service pointer is published by the host after native
        // context activation. These original handlers use RDX as their service
        // argument and do not consume the incoming RCX. No replies are forged.
        emit({0x48,0xb8}); value(remote + 208); emit({0x48,0x8b,0x10,0x48,0x85,0xd2,0x0f,0x84});
        const auto no_service = code.size(); value(int32_t{0});
        emit({0x48,0xb8}); value(image + 0x2f5e9c8); emit({0x8b,0x00,0x48,0xb9}); value(remote + 224); emit({0x89,0x01});
        for (auto [function, counter] : {std::pair<uint64_t,unsigned>{0x681870,216}, {0x682250,220}}) {
            emit({0x48,0xb8}); value(remote + 208); emit({0x48,0x8b,0x10,0x33,0xc9,0x48,0xb8}); value(image + function);
            emit({0xff,0xd0,0x48,0xb8}); value(remote + counter); emit({0xff,0x00});
        }
        const auto relative = static_cast<int32_t>(code.size() - no_service - 4); memcpy(code.data() + no_service, &relative, 4);
    }
    std::vector<size_t> outside_loading;
    if (context_tick) {
        if (resource_probe) {
            // Observe the state immediately around our native call. The host's
            // half-second sampling can miss a short transition or reset.
            emit({0x48,0xb8}); value(world); emit({0x0f,0xb6,0x50,0x18,0x48,0xb9}); value(remote);
            emit({0x88,0x51,0x4a,0x48,0x83,0x78,0x20,0,0x0f,0x84});
            outside_loading.push_back(code.size()); value(int32_t{0});
            emit({0x80,0xfa,2,0x0f,0x82}); outside_loading.push_back(code.size()); value(int32_t{0});
            emit({0x80,0xfa,4,0x0f,0x87}); outside_loading.push_back(code.size()); value(int32_t{0});
            for (unsigned state = 2; state <= 4; ++state) {
                emit({0x80,0xfa,static_cast<unsigned char>(state)}); const auto other_state = branch();
                emit({0xff,0x41,static_cast<unsigned char>(80 + (state - 2) * 4)});
                const auto relative = static_cast<int32_t>(code.size() - other_state - 4);
                memcpy(code.data() + other_state, &relative, 4);
            }
        }
        std::vector<size_t> called;
        if (loader_probe || resource_probe) {
            emit({0x48,0xb9}); value(uint64_t{0x0790000000000688});
            emit({0x48,0xb8}); value(image + 0x171b800); emit({0xff,0xd0,0x48,0xb9}); value(remote);
            emit({0x88,0x41,0x38});
            // Existence and residency are separate native queries. Preserve
            // the raw load-state byte; its enum is not yet established.
            emit({0x48,0xb9}); value(uint64_t{0x0790000000000688});
            emit({0x48,0xb8}); value(image + 0x171c0b0); emit({0xff,0xd0,0x48,0xb9}); value(remote);
            emit({0x88,0x41,0x39,0xc6,0x41,0x3a,1});
            emit({0x48,0xb8}); value(image + 0x321f338); emit({0x48,0x8b,0x08,0x48,0xba});
            value(uint64_t{0x0790000000000688}); emit({0x48,0xb8}); value(image + 0x1734310);
            emit({0xff,0xd0,0x48,0xb9}); value(remote); emit({0x48,0x89,0x41,0x68});
        }
        if (loader_probe) {
            // Follow only the original state table's loading handlers (2..4).
            // Each handler owns its transition; replication is not advanced.
            for (auto [state, function] : {std::pair<unsigned,uint64_t>{2,0xb52b20}, {3,0xb523f0}, {4,0xb4ff60}}) {
                emit({0x48,0xb8}); value(world); emit({0x80,0x78,0x18,static_cast<unsigned char>(state)});
                const auto other_state = branch();
                emit({0x48,0xb9}); value(world); emit({0x48,0xb8}); value(image + function); emit({0xff,0xd0,0xe9});
                called.push_back(code.size()); value(int32_t{0});
                const auto relative = static_cast<int32_t>(code.size() - other_state - 4);
                memcpy(code.data() + other_state, &relative, 4);
            }
            emit({0xe9}); const auto no_handler = code.size(); value(int32_t{0});
            const auto returned = code.size();
            for (auto at : called) {
                const auto relative = static_cast<int32_t>(returned - at - 4); memcpy(code.data() + at, &relative, 4);
            }
            emit({0x48,0xb8}); value(remote); emit({0xf0,0xff,0x40,0x30});
            const auto relative = static_cast<int32_t>(code.size() - no_handler - 4);
            memcpy(code.data() + no_handler, &relative, 4);
        } else {
        emit({0x48,0xb9}); value(world);
        emit({0xba,0,0,0,0x3f,0x66,0x0f,0x6e,0xca,0x48,0xb8}); value(image + tick); emit({0xff,0xd0});
        emit({0x48,0xb8}); value(remote); emit({0xf0,0xff,0x40,0x30});
        }
        if (resource_probe) {
            emit({0x48,0xb8}); value(world); emit({0x0f,0xb6,0x50,0x18,0x48,0xb9}); value(remote);
            emit({0x88,0x51,0x4b,0xc6,0x41,0x4d,1,0x3a,0x51,0x4c,0x76,3,0x88,0x51,0x4c});
            // Observe at most one additional update while the native world is
            // still at state 4, before resuming the original title/login loop.
            // All native loading gates remain in the original full update.
            emit({0x80,0xfa,4}); const auto not_map_loading = branch();
            emit({0x80,0x79,0x5e,0}); const auto already_repeated = branch();
            emit({0xc6,0x41,0x5e,1,0xe9}); const auto repeat = code.size(); value(int32_t{0});
            const auto repeat_relative = static_cast<int32_t>(pump - repeat - 4);
            memcpy(code.data() + repeat, &repeat_relative, 4);
            for (auto at : {not_map_loading, already_repeated}) {
                const auto relative = static_cast<int32_t>(code.size() - at - 4); memcpy(code.data() + at, &relative, 4);
            }
        }
    }
    const auto restore = code.size();
    for (auto at : outside_loading) {
        const auto relative = static_cast<int32_t>(restore - at - 4);
        memcpy(code.data() + at, &relative, 4);
    }
    for (auto at : {other_world, already_done, registration_failed}) {
        const auto target = at == already_done && context_tick ? pump : restore;
        const auto relative = static_cast<int32_t>(target - at - 4); memcpy(code.data() + at, &relative, 4);
    }
    for (unsigned reg = 0; reg < 4; ++reg) emit({0xf3,0x0f,0x6f,static_cast<unsigned char>(0x44 + reg * 8),0x24,static_cast<unsigned char>(0x40 + reg * 16)});
    emit({0x48,0x8b,0x4c,0x24,0x20,0x48,0x8b,0x54,0x24,0x28,0x4c,0x8b,0x44,0x24,0x30,0x4c,0x8b,0x4c,0x24,0x38});
    emit({0x48,0x81,0xc4,0xd8,0,0,0});
    if (context_probe) {
        emit({0x48,0xb8}); value(remote); emit({0xc7,0x40,0x60,0,0,0,0});
        emit({0x48,0xb9}); value(remote + 4096); emit({0x33,0xd2,0x48,0xb8});
        value(child_function_table_api(process, "NtContinue")); emit({0xff,0xe0});
    } else if (tick_probe) { emit({0x48,0xb8}); value(image + tick); emit({0xff,0xe0}); }
    else emit({0x33,0xc0,0xc3});
    if (code_offset + code.size() >= config_offset) throw std::runtime_error("Final callback code bounds");
    memcpy(page + code_offset, code.data(), code.size());
    RUNTIME_FUNCTION entry{code_offset, static_cast<DWORD>(code_offset + code.size()), unwind_offset}; memcpy(page + table_offset, &entry, sizeof(entry));
    if (!WriteProcessMemory(process, reinterpret_cast<void*>(remote), page, sizeof(page), &count) || count != sizeof(page))
        throw std::runtime_error("Final callback write failed");
    DWORD ignored = 0;
    if (!VirtualProtectEx(process, reinterpret_cast<void*>(remote), 4096, PAGE_EXECUTE_READWRITE, &ignored)
        || !FlushInstructionCache(process, reinterpret_cast<void*>(remote + code_offset), code.size()))
        throw std::runtime_error("Final callback execute protection failed");
    std::unique_ptr<void, decltype(&CloseHandle)> worker_handle(nullptr, CloseHandle);
    std::unique_ptr<PrimarySubmission> primary;
    if (context_probe) {
        // Redirect only at NtDelayExecution's verified post-syscall RET. Native
        // NtContinue restores the complete captured context, on the old stack.
        // Submission-only mode uses a 60 KiB scratch stack. Loading modes use
        // verified free space below the original stack, preserving native stack
        // probing, and refuse to reenter an active callback.
        primary = std::make_unique<PrimarySubmission>(process, primary_thread, remote, context_tick);
        bool redirected = false;
        std::cout << "Waiting for verified primary-thread delay return." << std::endl;
        for (unsigned attempt = 0; attempt < 6000 && !redirected; ++attempt) {
            redirected = primary->schedule(world, remote + code_offset);
            if (!redirected) Sleep(10);
        }
        if (!redirected) throw std::runtime_error("Final primary thread not at verified delay return");
        std::cout << "Final native request scheduled at verified primary-thread delay return." << std::endl;
    } else if (tick_probe) {
        replace_callback(process, world, image + vtable, remote + dispatch_offset);
        std::cout << "Final Practice request callback installed on native world tick." << std::endl;
    } else if (worker_probe) {
        worker_handle.reset(CreateRemoteThread(process, nullptr, 0,
            reinterpret_cast<LPTHREAD_START_ROUTINE>(remote + code_offset), reinterpret_cast<void*>(world), 0, nullptr));
        if (!worker_handle) throw std::runtime_error("Final diagnostic worker creation failed");
        std::cout << "Final Practice API worker started, tid=" << GetThreadId(worker_handle.get())
            << "; game-thread integration remains unverified." << std::endl;
    } else {
        HANDLE thread = OpenThread(THREAD_SET_CONTEXT | THREAD_QUERY_INFORMATION, FALSE, primary_thread);
        if (!thread || GetProcessIdOfThread(thread) != GetProcessId(process)) {
            if (thread) CloseHandle(thread);
            throw std::runtime_error("Final primary thread identity differs");
        }
        const auto queued = QueueUserAPC(reinterpret_cast<PAPCFUNC>(remote + code_offset), thread, world);
        CloseHandle(thread);
        if (!queued) throw std::runtime_error("Final request APC queue failed");
        std::cout << "Final Practice APC queued to primary thread; native request execution pending." << std::endl;
    }
    bool submitted = false; int previous = -1; uint32_t previous_completion = ~uint32_t{0};
    for (unsigned n = 0; n < 240; ++n) {
        if (WaitForSingleObject(process, 500) == WAIT_OBJECT_0) break;
        const auto completion = read_child<uint32_t>(process, remote);
        if (completion != previous_completion) {
            std::cout << "Final submission callback completion=" << completion << " entered="
                << read_child<uint32_t>(process, remote + 4) << " unwind_registered="
                << unsigned(read_child<unsigned char>(process, remote + 8)) << std::endl;
            previous_completion = completion;
        }
        if (completion == 2 && !read_child<unsigned char>(process, remote + 8))
            throw std::runtime_error("Final callback unwind registration failed");
        if (completion == 2 && !submitted) {
            if (read_child<uint64_t>(process, world) != (tick_probe ? remote + dispatch_offset : image + vtable))
                throw std::runtime_error("Final original world dispatch identity changed");
            submitted = true;
            const auto descriptor = read_child<uint64_t>(process, remote + 16);
            if (!descriptor || descriptor == remote + config_offset || read_child<uint32_t>(process, remote + 24) != practice_index)
                throw std::runtime_error("Native final request ownership/index differs");
            std::cout << "Native-owned Practice descriptor published." << std::endl;
            if (resource_probe)
                std::cout << "Native Practice header resource request returned=0x" << std::hex
                    << read_child<uint64_t>(process, remote + 64) << std::dec
                    << " attempted=" << unsigned(read_child<unsigned char>(process, remote + 72)) << std::endl;
            if (loading_context_probe)
                std::cout << "Native loading context constructor returned=0x" << std::hex
                    << read_child<uint64_t>(process, remote + 176) << std::dec
                    << " validated=" << unsigned(read_child<unsigned char>(process, remote + 195))
                    << " activated=" << unsigned(read_child<unsigned char>(process, remote + 193)) << std::endl;
            if (metadata_probe) {
                if (!read_child<unsigned char>(process, remote + 194) || !read_child<unsigned char>(process, remote + 193))
                    throw std::runtime_error("Native context activation required for metadata probe");
                const auto service = find_context_service(process, image, read_child<uint64_t>(process, remote + 176));
                if (!WriteProcessMemory(process, reinterpret_cast<void*>(remote + 208), &service, sizeof(service), &count) || count != sizeof(service))
                    throw std::runtime_error("Final metadata service diagnostic publication failed");
                std::cout << "Native metadata service verified for original initialization/processing handlers." << std::endl;
            }
            if (tick_probe) {
                replace_callback(process, world, remote + dispatch_offset, image + vtable);
                std::cout << "Original final world tick restored after native submission." << std::endl;
            }
        }
        const auto state = read_child<unsigned char>(process, world + 0x18);
        if (state != previous) {
            std::cout << "Final native world state=" << unsigned(state) << " request_descriptor=0x" << std::hex
                << read_child<uint64_t>(process, world + 0x20) << std::dec << std::endl; previous = state;
        }
        if (resource_probe && submitted && !read_child<uint64_t>(process, world + 0x20)
            && read_child<unsigned char>(process, remote + 77)) {
            std::cout << "Native loading cleared its request; stopping extra updates." << std::endl;
            break;
        }
        // Resource experiments stop our updates after native loading. Later
        // activation/replication needs its own verified session integration.
        if (context_tick && submitted && (!resource_probe || (state >= 2 && state <= 4))) primary->schedule(world, remote + code_offset);
        if (context_tick && n % 20 == 19)
            std::cout << "Final loading callbacks returned=" << read_child<uint32_t>(process, remote + 48)
                << " active=" << read_child<uint32_t>(process, remote + 96)
                << " native_Practice_header_available=" << unsigned(read_child<unsigned char>(process, remote + 56))
                << " native_Practice_header_load_state=" << unsigned(read_child<unsigned char>(process, remote + 57))
                << " native_header_index_entry=0x" << std::hex << read_child<uint64_t>(process, remote + 104) << std::dec << std::endl;
        if (resource_probe && n % 20 == 19)
            std::cout << "Final native update states before=" << unsigned(read_child<unsigned char>(process, remote + 74))
                << " after=" << unsigned(read_child<unsigned char>(process, remote + 75))
                << " highest_returned=" << unsigned(read_child<unsigned char>(process, remote + 76))
                << " calls_from_2=" << read_child<uint32_t>(process, remote + 80)
                << " calls_from_3=" << read_child<uint32_t>(process, remote + 84)
                << " calls_from_4=" << read_child<uint32_t>(process, remote + 88) << std::endl;
        if (metadata_probe && n % 20 == 19)
            std::cout << "Native metadata handlers returned initialization=" << read_child<uint32_t>(process, remote + 216)
                << " processing=" << read_child<uint32_t>(process, remote + 220)
                << " retained_request_submitted=" << unsigned(read_child<unsigned char>(process, remote + 202)) << std::endl;
    }
    if (tick_probe && !submitted && WaitForSingleObject(process, 0) == WAIT_TIMEOUT)
        replace_callback(process, world, remote + dispatch_offset, image + vtable);
    if (WaitForSingleObject(process, 0) == WAIT_TIMEOUT)
        std::cout << "Final callback entered=" << read_child<uint32_t>(process, remote + 4)
            << " entry_rcx=0x" << std::hex << read_child<uint64_t>(process, remote + 32)
            << " expected_world=0x" << world << std::dec << std::endl;
    if (context_tick && WaitForSingleObject(process, 0) == WAIT_TIMEOUT)
        std::cout << "Final original world updates returned=" << read_child<uint32_t>(process, remote + 48) << std::endl;
    std::cout << "Final native request submitted=" << submitted << std::endl;
    if (worker_handle) {
        DWORD exit_code = 0;
        if (GetExitCodeThread(worker_handle.get(), &exit_code))
            std::cout << "Final diagnostic worker status=0x" << std::hex << exit_code << std::dec << std::endl;
    }
    // Registered callback storage remains allocated until the owned job ends.
}
}
