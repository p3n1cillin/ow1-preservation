#pragma once

// Owned exact-build loopback diagnostic. Retain a guarded native connection job
// until bounded job exit, then read socket/job state. No debugger attachment,
// code patches, callback replacement or verdict/readiness writes.
namespace retail_tls_observer {
constexpr uint64_t socket_vtable = 0x298bed8, wrapper_vtable = 0x2a5c2c0;
struct Socket { uint64_t address = 0, wrapper = 0, transport = 0; };
struct Job { uint64_t address = 0, control = 0; };

Job find_job(HANDLE process, uint64_t image, uint64_t key) {
    const auto root = read_child<uint64_t>(process, image + 0x32c7af8);
    const auto buckets = read_child<uint64_t>(process, root), table = read_child<uint64_t>(process, root + 8);
    if (!buckets || buckets > 65536 || (buckets & (buckets - 1)) || !table) throw std::runtime_error("TLS job map bounds");
    uint64_t hash = key;
    hash ^= hash >> 33; hash *= 0xff51afd7ed558ccdULL;
    hash ^= hash >> 33; hash *= 0xc4ceb9fe1a85ec53ULL; hash ^= hash >> 33;
    auto node = read_child<uint64_t>(process, table + 8 * (hash & (buckets - 1)));
    for (unsigned count = 0; node && count < 128; ++count) {
        if (read_child<uint64_t>(process, node + 8) == key) {
            Job job{read_child<uint64_t>(process, node + 0x10), read_child<uint64_t>(process, node + 0x18)};
            if (!job.address || !job.control) return {};
            const auto vft = read_child<uint64_t>(process, job.address);
            if (vft != image + 0x29a5fa8
                || read_child<uint64_t>(process, job.control) != image + 0x29ac640) return {};
            const auto strong = read_child<uint32_t>(process, job.control + 8), weak = read_child<uint32_t>(process, job.control + 12);
            if (!strong || strong > 1000000 || !weak || weak > 1000000) return {};
            return job;
        }
        node = read_child<uint64_t>(process, node);
    }
    if (node) throw std::runtime_error("TLS job map chain budget");
    return {};
}

uint64_t find_key(HANDLE process, uint64_t image, const Socket& socket, std::stop_token stop) {
    MEMORY_BASIC_INFORMATION region{}; uint64_t cursor = 0, scanned = 0, found = 0;
    const auto deadline = GetTickCount64() + 15000;
    while (!stop.stop_requested() && VirtualQueryEx(process, reinterpret_cast<void*>(cursor), &region, sizeof(region))) {
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress), size = uint64_t(region.RegionSize);
        if (!size || start + size <= cursor) break; cursor = start + size;
        if (GetTickCount64() > deadline) throw std::runtime_error("TLS connection search deadline");
        if (region.State != MEM_COMMIT || region.Type != MEM_PRIVATE || (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            || !(region.Protect & (PAGE_READWRITE | PAGE_WRITECOPY))) continue;
        for (uint64_t offset = 0; offset < size && !stop.stop_requested(); offset += 1024 * 1024) {
            const auto bytes = SIZE_T(std::min<uint64_t>(size - offset, 1024 * 1024 + 7));
            if ((scanned += bytes) > 4ULL * 1024 * 1024 * 1024) throw std::runtime_error("TLS connection search budget");
            std::vector<unsigned char> block(bytes); SIZE_T count = 0;
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(start + offset), block.data(), bytes, &count) || count != bytes) continue;
            for (size_t at = 0; at + 8 <= bytes && at < 1024 * 1024; at += 8) {
                uint64_t value = 0; memcpy(&value, block.data() + at, 8);
                if (value != socket.address || start + offset + at < 0x48) continue;
                uint64_t key = 0;
                try {
                    const auto connection = start + offset + at - 0x48;
                    const auto factory = read_child<uint64_t>(process, connection + 8);
                    if (!factory || read_child<uint64_t>(process, factory) != image + 0x298e9b0) continue;
                    key = read_child<uint64_t>(process, connection + 0x18);
                    if (!key || !find_job(process, image, key).address) continue;
                } catch (const std::exception&) { continue; }
                if (found && found != key) throw std::runtime_error("TLS connection key is ambiguous");
                found = key;
            }
        }
    }
    return found;
}

Socket inspect(HANDLE process, uint64_t image, uint64_t address, bool live_ssl) {
    if (read_child<uint64_t>(process, address) != image + socket_vtable) return {};
    const auto wrapper = read_child<uint64_t>(process, address + 0x20);
    if (!wrapper || wrapper >= 0x800000000000 || wrapper % 8
        || read_child<uint64_t>(process, wrapper) != image + wrapper_vtable) return {};
    const auto transport = read_child<uint64_t>(process, wrapper + 8);
    if (!transport || transport >= 0x800000000000 || transport % 8
        || read_child<uint64_t>(process, transport) != image + retail_ca_probe::transport_vtable) return {};
    if (live_ssl && (!retail_ca_probe::inspect(process, image, transport).context
        || read_child<uint64_t>(process, wrapper + 0x40) != image + 0x216d040
        || read_child<uint64_t>(process, wrapper + 0x48) != image + 0x22478d0
        || read_child<uint64_t>(process, wrapper + 0x50) != address)) return {};
    return {address, wrapper, transport};
}

Socket find(HANDLE process, uint64_t image, std::stop_token stop) {
    MEMORY_BASIC_INFORMATION region{}; uint64_t cursor = 0, scanned = 0;
    const auto deadline = GetTickCount64() + 15000; Socket found;
    while (!stop.stop_requested() && VirtualQueryEx(process, reinterpret_cast<void*>(cursor), &region, sizeof(region))) {
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress), size = uint64_t(region.RegionSize);
        if (!size || start + size <= cursor) break;
        cursor = start + size;
        if (GetTickCount64() > deadline) throw std::runtime_error("TLS socket search deadline");
        if (region.State != MEM_COMMIT || region.Type != MEM_PRIVATE || (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            || !(region.Protect & (PAGE_READWRITE | PAGE_WRITECOPY))) continue;
        for (uint64_t offset = 0; offset < size && !stop.stop_requested(); offset += 1024 * 1024) {
            const auto bytes = SIZE_T(std::min<uint64_t>(size - offset, 1024 * 1024 + 7));
            if ((scanned += bytes) > 4ULL * 1024 * 1024 * 1024) throw std::runtime_error("TLS socket search budget");
            std::vector<unsigned char> block(bytes); SIZE_T count = 0;
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(start + offset), block.data(), bytes, &count) || count != bytes) continue;
            for (size_t at = 0; at + 8 <= bytes && at < 1024 * 1024; at += 8) {
                uint64_t value = 0; memcpy(&value, block.data() + at, 8);
                if (value != image + socket_vtable) continue;
                Socket candidate;
                try { candidate = inspect(process, image, start + offset + at, true); } catch (const std::exception&) { continue; }
                if (!candidate.address) continue;
                if (found.address && found.address != candidate.address) throw std::runtime_error("TLS observer requires one live original socket");
                found = candidate;
            }
        }
    }
    return found;
}

void install_ca(HANDLE process, uint64_t image, DWORD tid, const Socket& socket, const Job& job, const std::string& pem) {
    using retail_world_probe::guard;
    guard(process, image, 0x216cd3f, {0x48,0x8b,0x41,0x28,0x48,0x8d,0x79,0x28});
    guard(process, image, 0x216cd70, {0x4c,0x8b,0x43,8,0x48,0x8b,0xcf,0x48,0x8b,0x13});
    guard(process, image, 0x21e2fa4, {0x83,0xb9,0x84,0,0,0,1});
    checked(read_child<uint64_t>(process, image + socket_vtable + 0x70) == image + 0x216cd30, "TLS original CA setter slot");
    checked(!pem.empty() && pem.size() <= 16384, "TLS public CA size");
    const auto remote = reinterpret_cast<uint64_t>(VirtualAllocEx(process, nullptr, 65536, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    checked(remote != 0, "TLS CA setter callback allocation");
    unsigned char page[4096]{}; memcpy(page + 60, "FSA1", 4);
    memcpy(page + 32, &socket.address, 8); memcpy(page + 40, &job.address, 8);
    const unsigned char unwind[] = {1,7,2,0,7,1,27,0}; memcpy(page + 128, unwind, 8);
    std::vector<unsigned char> code; std::vector<size_t> skips;
    auto emit = [&](std::initializer_list<unsigned char> b) { code.insert(code.end(), b); };
    auto value = [&](uint64_t item) { auto p = reinterpret_cast<unsigned char*>(&item); code.insert(code.end(), p, p + 8); };
    auto call = [&](uint64_t target) { emit({0x48,0xb8}); value(target); emit({0xff,0xd0}); };
    auto skip = [&](unsigned char condition) { emit({0x0f,condition,0,0,0,0}); skips.push_back(code.size()-4); };
    auto identity = [&](uint64_t address, uint64_t expected) {
        emit({0x48,0xb9}); value(address); emit({0x48,0xb8}); value(expected); emit({0x48,0x39,0x01}); skip(0x85);
    };
    auto state = [&](uint64_t address, unsigned char expected) {
        emit({0x48,0xb9}); value(address); emit({0x83,0x39,expected}); skip(0x85);
    };
    emit({0x48,0x81,0xec,0xd8,0,0,0,0x48,0xb8}); value(remote);
    emit({0xff,0x40,4,0xc7,0x40,0x60,1,0,0,0});
    emit({0x48,0xb9}); value(remote+160); emit({0xba,1,0,0,0,0x49,0xb8}); value(remote); call(child_function_table_api(process));
    emit({0x48,0xb9}); value(remote); emit({0x88,0x41,8,0x84,0xc0}); skip(0x84);
    // Reject an ended or already-verifying socket/job at callback entry.
    identity(socket.address, image + socket_vtable);
    identity(socket.address + 0x20, socket.wrapper);
    identity(socket.wrapper, image + wrapper_vtable);
    identity(socket.wrapper + 8, socket.transport);
    identity(job.address, image + 0x29a5fa8);
    identity(job.control, image + 0x29ac640);
    state(socket.address + 0x50, 1); state(job.address + 0x80, 1); state(job.address + 0x88, 0);
    emit({0x48,0xb9}); value(remote); emit({0xc6,0x41,0x0c,1});
    emit({0x48,0xb9}); value(socket.address); emit({0x48,0x8b,0x41,0x30,0x48,0xba}); value(remote); emit({0x48,0x89,0x42,0x18});
    emit({0x48,0xba}); value(remote+6208); call(image+0x216cd30);
    emit({0x48,0xb9}); value(remote); emit({0x88,0x41,0x10});
    // Original getter used by the bgs hostname check; output is the connected
    // peer's address text, never an account/token/response string.
    emit({0x48,0xb9}); value(job.address); emit({0x48,0xba}); value(remote+6400); emit({0x41,0xb8,0,1,0,0}); call(image+0x21e2fa0);
    emit({0x48,0xb9}); value(remote); emit({0x88,0x41,0x11});
    for (auto at : skips) { auto displacement = int32_t(code.size()-at-4); memcpy(code.data()+at, &displacement, 4); }
    emit({0x48,0xb8}); value(remote); emit({0xc7,0,2,0,0,0,0xc7,0x40,0x60,0,0,0,0,0x48,0x81,0xc4,0xd8,0,0,0});
    emit({0x48,0xb9}); value(remote+4096); emit({0x33,0xd2}); call(child_function_table_api(process,"NtContinue")); emit({0xcc});
    checked(code.size()+256 < 2048, "TLS CA setter callback bounds"); memcpy(page+256,code.data(),code.size());
    RUNTIME_FUNCTION entry{256,DWORD(256+code.size()),128}; memcpy(page+160,&entry,sizeof(entry));
    // The original setter reads a span of 40-byte native string records, then
    // appends into its own allocated string. Author PEM memory is not adopted.
    uint64_t record[5]{remote+8192,pem.size(),0x8000000000000000ULL|pem.size(),0,0};
    uint64_t span[3]{remote+6144,1,0x8000000000000001ULL}; SIZE_T count = 0;
    auto write = [&](uint64_t target,const void* bytes,SIZE_T length) {
        checked(WriteProcessMemory(process,reinterpret_cast<void*>(target),bytes,length,&count) && count==length,"TLS CA setter author data write");
    };
    write(remote,page,4096); write(remote+6144,record,sizeof(record)); write(remote+6208,span,sizeof(span)); write(remote+8192,pem.c_str(),pem.size()+1);
    DWORD old = 0; checked(VirtualProtectEx(process,reinterpret_cast<void*>(remote),4096,PAGE_EXECUTE_READWRITE,&old),"TLS CA setter author code protection");
    checked(FlushInstructionCache(process,reinterpret_cast<void*>(remote+256),code.size()),"TLS CA setter author code cache");
    retail_world_probe::PrimarySubmission primary(process,tid,remote,true);
    // 15 s: the client may hold its primary thread suspended for a while.
    bool submitted = false; const auto deadline = GetTickCount64()+15000;
    while (WaitForSingleObject(process,10)==WAIT_TIMEOUT && GetTickCount64()<deadline) {
        if (!submitted) submitted = primary.schedule(socket.address,remote+256);
        if (read_child<uint32_t>(process,remote)!=2) continue;
        const auto passed = read_child<unsigned char>(process,remote+12), returned = read_child<unsigned char>(process,remote+16);
        bool matches = false; uint64_t bytes = 0;
        const auto current = inspect(process,image,socket.address,false);
        if (current.wrapper==socket.wrapper && current.transport==socket.transport) {
            bytes = read_child<uint64_t>(process,socket.address+0x30);
            if (bytes==pem.size()) {
                std::string actual(bytes,'\0'); const auto data = read_child<uint64_t>(process,socket.address+0x28);
                matches = ReadProcessMemory(process,reinterpret_cast<void*>(data),actual.data(),actual.size(),&count) && count==actual.size() && actual==pem;
            }
        }
        std::cout << "TLS CA setter: callback returned guard_passed=" << unsigned(passed) << " setter_result=" << unsigned(returned)
                  << " previous_ca_bytes=" << read_child<uint64_t>(process,remote+24) << " current_ca_bytes=" << bytes
                  << " public_pem_matches=" << matches << std::endl;
        if (read_child<unsigned char>(process,remote+17)) {
            char name[256]{};
            checked(ReadProcessMemory(process,reinterpret_cast<void*>(remote+6400),name,sizeof(name),&count) && count==sizeof(name),"TLS original peer-name read");
            const auto length = strnlen(name,sizeof(name));
            checked(length < sizeof(name),"TLS original peer-name bounds");
            std::cout << "TLS CA setter: original expected peer name=" << std::string(name,length) << std::endl;
        }
        checked(passed && returned && matches,"TLS original CA input was not installed"); return;
    }
    throw std::runtime_error("TLS CA setter ended before guarded callback completion");
}

void run(HANDLE process, uint64_t image, std::stop_token stop, DWORD primary_tid = 0, const std::string& socket_ca = {}) {
    using retail_world_probe::guard;
    const auto deadline = GetTickCount64() + 45000;
    bool ready = false;
    while (!stop.stop_requested() && WaitForSingleObject(process, 100) == WAIT_TIMEOUT && GetTickCount64() < deadline) {
        try {
            guard(process, image, 0x216c8a7, {0x8b,0x49,0x50});
            guard(process, image, 0x216d051, {0xc7,0x40,0x50,2,0,0,0});
            guard(process, image, 0x216d065, {0xc7,0x40,0x50,3,0,0,0});
            guard(process, image, 0x216d070, {0xc7,0x40,0x50,4,0,0,0});
            guard(process, image, 0x216cf95, {0x83,0x79,0x50,2});
            guard(process, image, 0x21e3310, {0x89,0x91,0x88,0,0,0});
            guard(process, image, 0x21e2fd0, {0x8b,0x81,0x80,0,0,0});
            guard(process, image, 0x21e3c60, {0x4c,0x8b,0x15,0x91,0x3e,0x0e,1});
            ready = true; break;
        } catch (const std::runtime_error&) { }
    }
    if (!ready || stop.stop_requested()) return;
    Socket socket;
    while (!stop.stop_requested() && WaitForSingleObject(process, 100) == WAIT_TIMEOUT) {
        socket = find(process, image, stop); if (socket.address) break;
    }
    if (!socket.address || stop.stop_requested()) return;
    std::cout << "TLS observer: original socket/wrapper/transport identities verified." << std::endl;
    const auto key = find_key(process, image, socket, stop);
    if (!key) throw std::runtime_error("TLS observer native connection job not found");
    std::cout << "TLS observer: original connection job identity verified." << std::endl;
    Job retained;
    {
        retail_ca_probe::Pause paused(process);
        retained = find_job(process, image, key);
        if (!retained.address) throw std::runtime_error("TLS connection job ended before retention");
        auto refs = read_child<uint32_t>(process, retained.control + 8) + 1; SIZE_T count = 0;
        checked(WriteProcessMemory(process, reinterpret_cast<void*>(retained.control + 8), &refs, 4, &count) && count == 4,
                "TLS observer retain original connection job");
    }
    std::cout << "TLS observer: original job reference retained until bounded process exit." << std::endl;
    if (!socket_ca.empty()) install_ca(process,image,primary_tid,socket,retained,socket_ca);
    uint32_t previous = UINT32_MAX; unsigned observations = 0;
    uint32_t previous_job = UINT32_MAX, previous_error = UINT32_MAX;
    bool socket_live = true;
    while (!stop.stop_requested() && WaitForSingleObject(process, 1) == WAIT_TIMEOUT) {
        try {
            const auto job = retained;
            if (read_child<uint64_t>(process, job.address) != image + 0x29a5fa8
                || read_child<uint64_t>(process, job.control) != image + 0x29ac640
                || !read_child<uint32_t>(process, job.control + 8)) throw std::runtime_error("TLS retained job identity differs");
            {
                const auto job_state = read_child<uint32_t>(process, job.address + 0x80), error = read_child<uint32_t>(process, job.address + 0x88);
                if (job_state != previous_job || error != previous_error) {
                    if (++observations > 32) throw std::runtime_error("TLS job observation budget exhausted");
                    std::cout << "TLS observer: native_job_state=" << job_state << " native_job_error=" << error << std::endl;
                    previous_job = job_state; previous_error = error;
                }
            }
            if (socket_live) {
                try {
                    const auto current = inspect(process, image, socket.address, false);
                    if (current.wrapper != socket.wrapper || current.transport != socket.transport)
                        throw std::runtime_error("original socket identity ended");
                    const auto state = read_child<uint32_t>(process, socket.address + 0x50);
                    if (state > 4) throw std::runtime_error("TLS socket state is outside original callback profile");
                    if (state != previous) {
                        if (++observations > 32) throw std::runtime_error("TLS socket observation budget exhausted");
                        const auto ca_bytes = read_child<uint64_t>(process, socket.address + 0x30);
                        if (ca_bytes > 1024 * 1024) throw std::runtime_error("TLS explicit CA input length bounds");
                        std::cout << "TLS observer: native_socket_state=" << state << " explicit_ca_input_bytes=" << ca_bytes << std::endl;
                        previous = state;
                    }
                } catch (const std::exception& error) {
                    socket_live = false;
                    std::cout << "TLS observer: socket observation ended: " << error.what() << std::endl;
                }
            }
        } catch (const std::exception& error) {
            if (stop.stop_requested() || WaitForSingleObject(process, 0) == WAIT_OBJECT_0) break;
            std::cout << "TLS observer: native job no longer readable/valid: " << error.what() << std::endl;
            return;
        }
    }
    std::cout << "TLS observer: observation ended; last_native_state=" << previous << std::endl;
}
}
