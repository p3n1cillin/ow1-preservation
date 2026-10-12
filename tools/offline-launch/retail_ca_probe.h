#pragma once
#include <tlhelp32.h>

// Exact 104319, bounded loopback diagnostic only. Add an operator-supplied
// public certificate through the original PEM parser / X509 store API. No
// verifier return values, TLS role/mode flags or executable bytes are changed.
// Included after retail_world_probe.h to reuse its guarded primary transport.
namespace retail_ca_probe {
constexpr uint64_t transport_vtable = 0x2a5c0e8, client_method = 0x2a617d0;

struct Session { uint64_t transport = 0, context = 0, ssl = 0, store = 0; };

Session inspect(HANDLE process, uint64_t image, uint64_t address) {
    if (read_child<uint64_t>(process, address) != image + transport_vtable) return {};
    const auto context = read_child<uint64_t>(process, address + 0x30);
    const auto ssl = read_child<uint64_t>(process, address + 0x38);
    auto pointer = [](uint64_t p) { return p && p < 0x800000000000 && !(p & 7); };
    if (!pointer(context) || !pointer(ssl)) return {};
    if (read_child<uint64_t>(process, context) != image + client_method
        || read_child<uint64_t>(process, ssl + 8) != image + client_method
        || read_child<uint64_t>(process, ssl + 0x598) != context
        || read_child<uint32_t>(process, ssl + 0x38) != 0) return {};
    const auto ctx_refs = read_child<uint32_t>(process, context + 0x94);
    const auto ssl_refs = read_child<uint32_t>(process, ssl + 0x5c8);
    const auto store = read_child<uint64_t>(process, context + 0x20);
    if (!ctx_refs || ctx_refs > 1000000 || !ssl_refs || ssl_refs > 1000000 || !pointer(store)) return {};
    return {address, context, ssl, store};
}

Session find(HANDLE process, uint64_t image, std::stop_token stop) {
    MEMORY_BASIC_INFORMATION region{}; uint64_t cursor = 0, scanned = 0;
    const auto deadline = GetTickCount64() + 15000; Session found;
    while (!stop.stop_requested() && VirtualQueryEx(process, reinterpret_cast<void*>(cursor), &region, sizeof(region))) {
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress), size = uint64_t(region.RegionSize);
        if (!size || start + size <= cursor) break;
        cursor = start + size;
        if (GetTickCount64() > deadline) throw std::runtime_error("CA session search deadline");
        if (region.State != MEM_COMMIT || region.Type != MEM_PRIVATE || (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            || !(region.Protect & (PAGE_READWRITE | PAGE_WRITECOPY))) continue;
        for (uint64_t offset = 0; offset < size && !stop.stop_requested(); offset += 1024 * 1024) {
            const auto bytes = SIZE_T(std::min<uint64_t>(size - offset, 1024 * 1024 + 7));
            if ((scanned += bytes) > 4ULL * 1024 * 1024 * 1024) throw std::runtime_error("CA session search budget");
            std::vector<unsigned char> block(bytes); SIZE_T count = 0;
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(start + offset), block.data(), bytes, &count) || count != bytes) continue;
            for (size_t at = 0; at + 8 <= bytes && at < 1024 * 1024; at += 8) {
                uint64_t value = 0; memcpy(&value, block.data() + at, 8);
                if (value != image + transport_vtable) continue;
                Session candidate;
                try { candidate = inspect(process, image, start + offset + at); } catch (const std::exception&) { continue; }
                if (!candidate.context) continue;
                if (found.transport && found.transport != candidate.transport) throw std::runtime_error("CA probe requires one live native TLS session");
                found = candidate;
            }
        }
    }
    return found;
}

// Freeze only this owned child while validating and retaining its SSL_CTX.
// Each successful SuspendThread is balanced, including constructor failures.
struct Pause {
    std::vector<std::pair<DWORD,HANDLE>> threads;
    std::vector<std::pair<DWORD,HANDLE>> already_paused;
    static uint32_t suspension(HANDLE thread) {
        using Query = NTSTATUS(NTAPI*)(HANDLE, ULONG, PVOID, ULONG, PULONG);
        const auto query = reinterpret_cast<Query>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationThread"));
        uint32_t count = 0;
        if (!query || query(thread, 35, &count, sizeof(count), nullptr) < 0)
            throw std::runtime_error("CA thread suspension query unavailable");
        return count;
    }
    explicit Pause(HANDLE process) {
        const auto pid = GetProcessId(process);
        try {
          // Allocate bookkeeping before acquiring any suspension ownership.
          threads.reserve(256); already_paused.reserve(256);
          bool stable = false;
          for (unsigned pass = 0; pass < 8; ++pass) {
            size_t added = 0;
            HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
            checked(snapshot != INVALID_HANDLE_VALUE, "CA thread snapshot");
            std::unique_ptr<void, decltype(&CloseHandle)> owned(snapshot, CloseHandle);
            THREADENTRY32 entry{}; entry.dwSize = sizeof(entry);
            checked(Thread32First(snapshot, &entry), "CA first thread entry");
            do {
                if (entry.th32OwnerProcessID != pid) continue;
                const auto known = [&](auto t) { return t.first == entry.th32ThreadID; };
                if (std::any_of(threads.begin(), threads.end(), known)
                    || std::any_of(already_paused.begin(), already_paused.end(), known)) continue;
                if (threads.size() + already_paused.size() >= 256) throw std::runtime_error("CA thread budget");
                HANDLE thread = OpenThread(THREAD_SUSPEND_RESUME | THREAD_QUERY_INFORMATION | SYNCHRONIZE, FALSE, entry.th32ThreadID);
                checked(thread != nullptr, "CA open owned thread");
                if (GetProcessIdOfThread(thread) != pid) { CloseHandle(thread); throw std::runtime_error("CA thread owner differs"); }
                uint32_t initial = 0;
                try { initial = suspension(thread); } catch (...) { CloseHandle(thread); throw; }
                if (initial) {
                    already_paused.emplace_back(entry.th32ThreadID, thread);
                    ++added;
                    continue; // Preserve the original count, including MAXIMUM_SUSPEND_COUNT.
                }
                const auto count = SuspendThread(thread);
                if (count == DWORD(-1)) {
                    const auto error = GetLastError();
                    const bool exited = WaitForSingleObject(thread, 0) == WAIT_OBJECT_0;
                    CloseHandle(thread);
                    if (exited) continue; // An exited thread cannot race the retained context.
                    throw std::runtime_error("CA pause owned thread Win32=" + std::to_string(error)
                                             + " tid=" + std::to_string(entry.th32ThreadID) + " initial_count=" + std::to_string(initial));
                }
                threads.emplace_back(entry.th32ThreadID, thread);
                ++added;
            } while (Thread32Next(snapshot, &entry));
            checked(GetLastError() == ERROR_NO_MORE_FILES, "CA complete thread inventory");
            if (!added) { stable = true; break; }
          }
            checked(!threads.empty(), "CA owned thread inventory empty");
            if (!stable) throw std::runtime_error("CA thread inventory did not stabilize; no mutation");
            for (auto [id, thread] : already_paused)
                if (!suspension(thread)) throw std::runtime_error("CA original suspension changed; no mutation");
            if (!already_paused.empty()) std::cout << "Native CA probe: preserved " << already_paused.size() << " already-suspended thread counts." << std::endl;
        } catch (...) { resume(); throw; }
    }
    void resume() {
        for (auto [id, thread] : threads) { ResumeThread(thread); CloseHandle(thread); } threads.clear();
        for (auto [id, thread] : already_paused) CloseHandle(thread); already_paused.clear();
    }
    ~Pause() { resume(); }
    Pause(const Pause&) = delete;
};

void run(HANDLE process, uint64_t image, DWORD tid, const std::string& pem, std::stop_token stop) {
    const auto started = GetTickCount64();
    using retail_world_probe::guard;
    const auto profile_ready = [&]() {
    guard(process, image, 0x236c98d, {0x48,0x8d,0x05,0x54,0xf7,0x6e,0});
    guard(process, image, 0x2388492, {0x8b,0x87,0x58,1,0,0,0x89,0x83,0x58,5,0,0});
    guard(process, image, 0x23885b5, {0x48,0x89,0xbb,0x98,5,0,0});
    guard(process, image, 0x2370090, {0x40,0x53,0x48,0x83,0xec,0x20,0x83,0xca,0xff});
    guard(process, image, 0x2385ae0, {0x48,0x83,0xec,0x38,0x45,0x33,0xc0});
    guard(process, image, 0x23863e0, {0x48,0x8d,0x15,0xa9,0x9e,0x6d,0});
    };
    bool ready = false;
    const auto deadline = GetTickCount64() + 45000;
    while (!stop.stop_requested() && WaitForSingleObject(process, 200) == WAIT_TIMEOUT && GetTickCount64() < deadline) {
        try { profile_ready(); ready = true; break; } catch (const std::runtime_error&) { }
    }
    if (!ready) throw std::runtime_error("CA original instruction profile unavailable");
    std::cout << "Native CA probe: original instruction profile verified." << std::endl;
    Session session;
    while (!stop.stop_requested() && WaitForSingleObject(process, 300) == WAIT_TIMEOUT) {
        session = find(process, image, stop);
        if (session.context) break;
    }
    if (!session.context || stop.stop_requested()) return;
    std::cout << "Native CA probe: one live TLS client context found, elapsed_ms=" << GetTickCount64() - started << std::endl;
    {
        Pause paused(process);
        const auto current = inspect(process, image, session.transport);
        checked(current.context == session.context && current.ssl == session.ssl && current.store == session.store, "CA session changed before retention");
        auto refs = read_child<uint32_t>(process, session.context + 0x94) + 1; SIZE_T count = 0;
        checked(WriteProcessMemory(process, reinterpret_cast<void*>(session.context + 0x94), &refs, 4, &count) && count == 4, "CA retain original SSL context");
    }
    // The retained reference and callback allocation live until this bounded
    // job exits. The original native API owns the inserted certificate ref.
    const auto remote = reinterpret_cast<uint64_t>(VirtualAllocEx(process, nullptr, 65536, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    checked(remote != 0, "CA callback allocation");
    unsigned char page[4096]{}; memcpy(page + 60, "FCA1", 4);
    memcpy(page + 32, &session.context, 8); memcpy(page + 40, &session.store, 8);
    const unsigned char unwind[] = {1,7,2,0,7,1,27,0}; memcpy(page + 128, unwind, 8);
    std::vector<unsigned char> code;
    auto emit = [&](std::initializer_list<unsigned char> bytes) { code.insert(code.end(), bytes); };
    auto value = [&](uint64_t item) { auto p = reinterpret_cast<unsigned char*>(&item); code.insert(code.end(), p, p + 8); };
    auto call = [&](uint64_t target) { emit({0x48,0xb8}); value(target); emit({0xff,0xd0}); };
    auto jz = [&]() { emit({0x0f,0x84,0,0,0,0}); return code.size() - 4; };
    emit({0x48,0x81,0xec,0xd8,0,0,0});
    emit({0x48,0xb8}); value(remote); emit({0xff,0x40,4,0xc7,0x40,0x60,1,0,0,0});
    emit({0x48,0xb9}); value(remote + 160); emit({0xba,1,0,0,0,0x49,0xb8}); value(remote);
    call(child_function_table_api(process));
    emit({0x48,0xb9}); value(remote); emit({0x88,0x41,8,0x84,0xc0}); const auto no_unwind = jz();
    emit({0x48,0xb9}); value(remote + 8192); call(image + 0x2370090);
    emit({0x48,0xb9}); value(remote); emit({0x48,0x89,0x41,0x10,0x48,0x85,0xc0}); const auto no_cert = jz();
    emit({0xc6,0x41,0x0c,1,0x48,0x89,0xc2,0x48,0xb9}); value(session.store); call(image + 0x2385ae0);
    emit({0x48,0xb9}); value(remote); emit({0x89,0x41,0x18,0x48,0x8b,0x49,0x10}); call(image + 0x23863e0);
    for (auto at : {no_unwind, no_cert}) { auto relative = int32_t(code.size() - at - 4); memcpy(code.data() + at, &relative, 4); }
    emit({0x48,0xb8}); value(remote); emit({0xc7,0x00,2,0,0,0,0xc7,0x40,0x60,0,0,0,0,0x48,0x81,0xc4,0xd8,0,0,0});
    emit({0x48,0xb9}); value(remote + 4096); emit({0x33,0xd2,0x48,0xb8}); value(child_function_table_api(process, "NtContinue")); emit({0xff,0xe0});
    checked(code.size() + 256 < 2048, "CA callback code bounds");
    memcpy(page + 256, code.data(), code.size());
    RUNTIME_FUNCTION entry{256, DWORD(256 + code.size()), 128}; memcpy(page + 160, &entry, sizeof(entry));
    SIZE_T count = 0;
    checked(WriteProcessMemory(process, reinterpret_cast<void*>(remote), page, 4096, &count) && count == 4096, "CA callback write");
    checked(WriteProcessMemory(process, reinterpret_cast<void*>(remote + 8192), pem.c_str(), pem.size() + 1, &count) && count == pem.size() + 1, "CA public certificate write");
    DWORD prior = 0; checked(VirtualProtectEx(process, reinterpret_cast<void*>(remote), 4096, PAGE_EXECUTE_READWRITE, &prior), "CA author callback protection");
    checked(FlushInstructionCache(process, reinterpret_cast<void*>(remote + 256), code.size()), "CA callback cache");
    retail_world_probe::PrimarySubmission primary(process, tid, remote, true);
    bool submitted = false;
    while (!stop.stop_requested() && WaitForSingleObject(process, 10) == WAIT_TIMEOUT) {
        if (!submitted) {
            submitted = primary.schedule(session.store, remote + 256);
            if (submitted) std::cout << "Native CA probe: primary-thread import scheduled, elapsed_ms=" << GetTickCount64() - started << std::endl;
        }
        if (read_child<uint32_t>(process, remote) == 2) {
            std::cout << "Native CA probe: callback returned, parsed=" << unsigned(read_child<unsigned char>(process, remote + 12))
                      << " inserted=" << read_child<uint32_t>(process, remote + 24)
                      << " unwind_registered=" << unsigned(read_child<unsigned char>(process, remote + 8))
                      << " elapsed_ms=" << GetTickCount64() - started
                      << "; TLS acceptance requires a real server handshake." << std::endl;
            return;
        }
    }
    std::cout << "Native CA probe ended before callback completion; submitted=" << submitted << std::endl;
}
}
