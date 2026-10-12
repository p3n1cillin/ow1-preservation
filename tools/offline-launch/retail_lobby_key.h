#pragma once

// One owned, exact-build, bounded loopback experiment. Replace only the heap
// modulus of a guarded lobby pipe with the operator's public RSA-2048 key.
// Original RSA/address/integrity verifiers and their results stay intact.
namespace retail_lobby_key {
constexpr uint64_t pipe_vtable = 0x2616130, key_vtable = 0x26569c8;
struct Number { int32_t used, allocated, sign, padding; uint64_t digits, reserved; };
struct Target { uint64_t pipe = 0, key = 0; Number modulus{}; };

std::vector<uint32_t> limbs(const std::string& bytes) {
    checked(bytes.size() == 256, "Lobby public modulus size");
    std::vector<uint32_t> result(74);
    for (unsigned bit = 0; bit < 2048; ++bit)
        if ((static_cast<unsigned char>(bytes[bit / 8]) >> (bit % 8)) & 1)
            result[bit / 28] |= uint32_t(1) << (bit % 28);
    return result;
}

bool writable(HANDLE process, uint64_t address, SIZE_T length) {
    MEMORY_BASIC_INFORMATION region{};
    if (!VirtualQueryEx(process, reinterpret_cast<void*>(address), &region, sizeof(region))) return false;
    const auto start = reinterpret_cast<uint64_t>(region.BaseAddress);
    return region.State == MEM_COMMIT && region.Type == MEM_PRIVATE
        && !(region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
        && (region.Protect & PAGE_READWRITE) && address >= start
        && length <= region.RegionSize && address - start <= region.RegionSize - length;
}

Target inspect(HANDLE process, uint64_t image, uint64_t pipe, const std::vector<uint32_t>& original) {
    if (!writable(process, pipe, 0x2e0) || read_child<uint64_t>(process, pipe) != image + pipe_vtable) return {};
    const auto state = read_child<uint32_t>(process, pipe + 0x80);
    if (state > 4 || !read_child<uint64_t>(process, pipe + 0x1a8)) return {};
    const auto key = read_child<uint64_t>(process, pipe + 0x28);
    if (!writable(process, key, 0x50) || read_child<uint64_t>(process, key) != image + key_vtable
        || read_child<uint64_t>(process, key + 8) != 256) return {};
    const auto number = read_child<Number>(process, key + 0x10);
    const auto exponent = read_child<Number>(process, key + 0x30);
    if (number.used != 74 || number.allocated < 74 || number.allocated > 128 || number.sign
        || !writable(process, number.digits, original.size()*4)
        || exponent.used != 1 || exponent.allocated < 1 || exponent.allocated > 8 || exponent.sign
        || !writable(process, exponent.digits, 4) || read_child<uint32_t>(process, exponent.digits) != 65537) return {};
    std::vector<uint32_t> actual(74); SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(number.digits), actual.data(), actual.size()*4, &count)
        || count != actual.size()*4 || actual != original) return {};
    return {pipe, key, number};
}

Target find(HANDLE process, uint64_t image, const std::vector<uint32_t>& original, std::stop_token stop) {
    uint64_t cursor = 0, scanned = 0; Target found; MEMORY_BASIC_INFORMATION region{};
    const auto deadline = GetTickCount64() + 15000;
    while (!stop.stop_requested() && VirtualQueryEx(process, reinterpret_cast<void*>(cursor), &region, sizeof(region))) {
        const auto start = reinterpret_cast<uint64_t>(region.BaseAddress), size = uint64_t(region.RegionSize);
        if (!size || start + size <= cursor) break; cursor = start + size;
        if (GetTickCount64() > deadline) throw std::runtime_error("Lobby key search deadline");
        if (region.State != MEM_COMMIT || region.Type != MEM_PRIVATE || (region.Protect & (PAGE_GUARD | PAGE_NOACCESS))
            || !(region.Protect & PAGE_READWRITE)) continue;
        for (uint64_t offset = 0; offset < size && !stop.stop_requested(); offset += 1024*1024) {
            const auto bytes = SIZE_T(std::min<uint64_t>(size-offset, 1024*1024+7));
            if ((scanned += bytes) > 4ULL*1024*1024*1024) throw std::runtime_error("Lobby key search budget");
            std::vector<unsigned char> block(bytes); SIZE_T count = 0;
            if (!ReadProcessMemory(process, reinterpret_cast<void*>(start+offset), block.data(), bytes, &count) || count != bytes) continue;
            for (size_t at = 0; at+8 <= bytes && at < 1024*1024; at += 8) {
                uint64_t value = 0; memcpy(&value, block.data()+at, 8);
                if (value != image+pipe_vtable) continue;
                Target candidate;
                try { candidate = inspect(process, image, start+offset+at, original); } catch (const std::exception&) { continue; }
                if (!candidate.pipe) continue;
                if (found.pipe && found.pipe != candidate.pipe) throw std::runtime_error("Lobby key owner is ambiguous");
                found = candidate;
            }
        }
    }
    return found;
}

uint64_t run(HANDLE process, uint64_t image, const std::string& public_modulus, std::stop_token stop) {
    using retail_world_probe::guard;
    guard(process, image, 0xe39066, {0x48,0x8b,0x4f,0x28});
    guard(process, image, 0x24d34d1, {0x4c,0x89,0x41,8,0x48,0x89,1});
    guard(process, image, 0x24d3561, {0x4c,0x8d,0x43,0x10,0x48,0x8d,0x4c,0x24,0x20});
    checked(read_child<uint64_t>(process, image+pipe_vtable+0x110) == image+0x7bf060, "Lobby pipe callback identity");
    std::string original_bytes(256, '\0'); SIZE_T count = 0;
    checked(ReadProcessMemory(process, reinterpret_cast<void*>(image+0x26779d0), original_bytes.data(), 256, &count)
        && count == 256, "Lobby original public modulus read");
    const auto original = limbs(original_bytes), replacement = limbs(public_modulus);
    checked(original != replacement, "Lobby operator key must differ from original key");
    const auto deadline = GetTickCount64() + 45000;
    while (!stop.stop_requested() && WaitForSingleObject(process, 100) == WAIT_TIMEOUT && GetTickCount64() < deadline) {
        const auto target = find(process, image, original, stop);
        if (!target.pipe || stop.stop_requested()) continue;
        retail_ca_probe::Pause paused(process);
        const auto current = inspect(process, image, target.pipe, original);
        if (current.key != target.key || current.modulus.digits != target.modulus.digits) continue;
        std::vector<uint32_t> actual(74);
        const bool written = WriteProcessMemory(process, reinterpret_cast<void*>(current.modulus.digits), replacement.data(), replacement.size()*4, &count)
            && count == replacement.size()*4;
        const bool verified = written && ReadProcessMemory(process, reinterpret_cast<void*>(current.modulus.digits), actual.data(), actual.size()*4, &count)
            && count == actual.size()*4 && actual == replacement;
        if (!verified) {
            // Restore the checked original under the same pause if a write or
            // readback fails. No resumed client sees an intentional partial key.
            checked(WriteProcessMemory(process, reinterpret_cast<void*>(current.modulus.digits), original.data(), original.size()*4, &count)
                && count == original.size()*4, "Lobby original modulus rollback");
            throw std::runtime_error("Lobby own public modulus installation/readback failed; original restored");
        }
        std::cout << "Lobby key: guarded heap modulus replaced with own RSA-2048/e=65537 public key; native_state="
                  << read_child<uint32_t>(process, current.pipe+0x80) << std::endl;
        // No ownership/layout changes: the original allocation/destructor remain.
        return current.pipe;
    }
    if (!stop.stop_requested()) throw std::runtime_error("Lobby key ended before guarded installation");
    return 0;
}
}
