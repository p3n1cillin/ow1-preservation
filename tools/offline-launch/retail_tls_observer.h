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

void run(HANDLE process, uint64_t image, std::stop_token stop) {
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
