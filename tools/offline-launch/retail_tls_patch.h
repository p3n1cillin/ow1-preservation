#pragma once
// Private-server bgs TLS acceptance patch for the final retail client.
//
// The bgs login RPC uses a statically-linked OpenSSL ("cross_ssl") whose trust
// is governed by an RSA-signed ServerInfo pin bundle baked into the client, so
// our own CA cannot satisfy it. Empirically the client (as TLS client) rejects
// our loopback server's certificate DURING the handshake: it sends its
// ClientHello, receives our ServerHello+Certificate, then closes before its
// own Finished. The rejection therefore happens in the in-handshake OpenSSL
// cert-verify callbacks (chain + public-key pinning), which are invoked
// indirectly through a stored function pointer and return a cross_ssl result
// code (0 = verified, nonzero = failure).
//
// To let the UNMODIFIED-ON-DISK client trust OUR OWN loopback login server, we
// patch, in memory only, the return value of those verify callbacks to report
// success. This is the established private-server technique for a client the
// user owns (cf. Plasmawatch OverLauncher for the beta). It does NOT forge
// Blizzard's ServerInfo signature and changes nothing on disk; only the
// process is confined to the launcher's explicitly forwarded loopback ports.
// The candidate changes the process-wide verifier, not a per-connection rule.
//
// The on-disk exe is packed; code is decrypted lazily, so we poll each site
// until its exact instruction window appears, then apply a two-byte patch
// (`mov eax, ebx` 8B C3 -> `xor eax, eax` 31 C0). RVAs are for the decrypted
// image (base 0x7ff794400000).
#include <windows.h>
#include <atomic>
#include <cstdint>
#include <iostream>
#include <vector>
#include <stop_token>

namespace retail_tls_patch {

struct Site {
    const char* name;
    uint64_t anchor_rva;                 // where the signature window begins
    std::vector<unsigned char> signature;// exact bytes expected once decrypted
    size_t patch_offset;                 // offset of the 2-byte patch in the window
    bool required;                       // a required site failing is reported prominently
};

inline const std::vector<Site>& sites() {
    static const std::vector<Site> s = {
        // In-handshake chain-verify callback return: mov eax,ebx; jmp +2; xor eax,eax.
        {"chain-verify", 0x217c3a9, {0x8b,0xc3,0xeb,0x02,0x33,0xc0}, 0, true},
        // In-handshake public-key-pinning callback return: nop; mov eax,ebx; mov rcx,[rsp+0x180].
        {"pin-verify", 0x217bb53, {0x90,0x8b,0xc3,0x48,0x8b,0x8c,0x24,0x80,0x01}, 1, true},
        // Post-handshake verdict aggregator return (reached only once the
        // handshake completes; best-effort, may stay encrypted until then).
        {"post-handshake-verdict", 0x236f1e0,
         {0x33,0xd2,0xff,0x54,0x24,0x30,0x8b,0xc3,0x48,0x8b,0x4c,0x24,0x48,0x48,0x33,0xcc,0xe8}, 6, false},
    };
    return s;
}

inline constexpr unsigned char patched[] = {0x31,0xc0}; // xor eax, eax

// Error 87 alone does not establish ACG. Query the policy of this owned child.
inline void report_policy(HANDLE process) {
    PROCESS_MITIGATION_DYNAMIC_CODE_POLICY policy{};
    if (GetProcessMitigationPolicy(process, ProcessDynamicCodePolicy, &policy, sizeof(policy)))
        std::cout << "bgs TLS diagnostic: dynamic-code policy flags=" << policy.Flags
                  << " prohibit=" << policy.ProhibitDynamicCode
                  << " thread_opt_out=" << policy.AllowThreadOptOut
                  << " remote_downgrade=" << policy.AllowRemoteDowngrade << std::endl;
    else std::cout << "bgs TLS diagnostic: mitigation query failed Win32=" << GetLastError() << std::endl;
}

inline bool patch_one(HANDLE process, uint64_t image, const Site& site) {
    const auto anchor = image + site.anchor_rva;
    std::vector<unsigned char> window(site.signature.size());
    SIZE_T count = 0;
    static std::vector<std::string> logged; // one failure log per site (single caller thread)
    auto log_once = [&](const std::string& msg) {
        const std::string key = std::string(site.name) + msg;
        for (const auto& k : logged) if (k == key) return;
        logged.push_back(key);
        std::cout << "bgs TLS patch: '" << site.name << "' " << msg << std::endl;
    };
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(anchor), window.data(), window.size(), &count)
        || count != window.size() || memcmp(window.data(), site.signature.data(), window.size()))
        return false;
    log_once("signature matched; attempting patch");
    const auto target = anchor + site.patch_offset;
    DWORD protect = 0, ignored = 0; SIZE_T written = 0;
    if (!VirtualProtectEx(process, reinterpret_cast<void*>(target), sizeof(patched), PAGE_EXECUTE_READWRITE, &protect)) {
        const auto error = GetLastError();
        log_once("VirtualProtectEx(RWX) failed Win32=" + std::to_string(error));
        return false;
    }
    const bool ok = WriteProcessMemory(process, reinterpret_cast<void*>(target), patched, sizeof(patched), &written)
        && written == sizeof(patched);
    const auto write_err = GetLastError();
    VirtualProtectEx(process, reinterpret_cast<void*>(target), sizeof(patched), protect, &ignored);
    FlushInstructionCache(process, reinterpret_cast<void*>(target), sizeof(patched));
    if (ok) std::cout << "bgs TLS patch: '" << site.name << "' forced to accept at RVA 0x"
                      << std::hex << site.anchor_rva << std::dec << " (in-memory; disk unchanged)." << std::endl;
    else log_once("WriteProcessMemory failed Win32=" + std::to_string(write_err));
    return ok;
}

// Diagnostic: classify why a required site never matched. Dumps the live bytes
// at the site and scans all committed executable memory for a position-
// independent signature of the function, to tell "encrypted in place" from
// "relocated to a copy we could patch elsewhere".
inline void diagnose(HANDLE process, uint64_t image, const Site& site) {
    report_policy(process);
    const auto anchor = image + site.anchor_rva;
    unsigned char live[16]{}; SIZE_T count = 0;
    MEMORY_BASIC_INFORMATION mbi{};
    const bool q = VirtualQueryEx(process, reinterpret_cast<void*>(anchor), &mbi, sizeof(mbi)) == sizeof(mbi);
    ReadProcessMemory(process, reinterpret_cast<void*>(anchor), live, sizeof(live), &count);
    std::cout << "  diag '" << site.name << "' RVA 0x" << std::hex << site.anchor_rva
              << " state=" << (q ? mbi.State : 0) << " protect=" << (q ? mbi.Protect : 0)
              << " type=" << (q ? mbi.Type : 0) << " allocation_protect=" << (q ? mbi.AllocationProtect : 0)
              << " live=" << std::dec;
    for (SIZE_T i = 0; i < count; ++i) { char b[4]; sprintf_s(b, "%02x", live[i]); std::cout << b; }
    std::cout << " (expected " ;
    for (auto b : site.signature) { char t[4]; sprintf_s(t, "%02x", b); std::cout << t; }
    std::cout << ")" << std::endl;
    // Scan committed executable regions for the signature.
    const auto& sig = site.signature;
    uint64_t addr = 0x10000; unsigned hits = 0;
    while (addr < 0x7fffffff0000ull && hits < 8) {
        if (VirtualQueryEx(process, reinterpret_cast<void*>(addr), &mbi, sizeof(mbi)) != sizeof(mbi)) break;
        const auto base = reinterpret_cast<uint64_t>(mbi.BaseAddress);
        const bool exec = mbi.State == MEM_COMMIT && (mbi.Protect & (PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY));
        if (exec && mbi.RegionSize <= 0x4000000) {
            std::vector<unsigned char> buf(mbi.RegionSize);
            SIZE_T got = 0;
            if (ReadProcessMemory(process, mbi.BaseAddress, buf.data(), buf.size(), &got) && got >= sig.size()) {
                for (size_t i = 0; i + sig.size() <= got; ++i) {
                    if (!memcmp(buf.data() + i, sig.data(), sig.size())) {
                        const auto found = base + i;
                        std::cout << "    sig found at 0x" << std::hex << found
                                  << (found == anchor ? " (== site)" : " (additional byte-pattern match)") << std::dec << std::endl;
                        if (++hits >= 8) break;
                    }
                }
            }
        }
        addr = base + mbi.RegionSize;
    }
    if (!hits) std::cout << "    signature not found in any executable region (encrypted/not resident)." << std::endl;
}

// Poll the child for the whole session until each site's packed code has
// decrypted in place, then patch it. The retail client decrypts this code
// lazily (only after it has initialized far enough, which is AFTER its first
// connection attempts), so we must keep watching and patch the moment the code
// is resident; the client's next bgs retry then uses the accepting verify.
// Does not throw; an interactive client is never torn down by a patch failure.
inline void apply(HANDLE process, uint64_t image, std::stop_token stop, unsigned timeout_ms = 900000) {
    report_policy(process);
    std::vector<bool> done(sites().size(), false);
    std::vector<bool> diagnosed(sites().size(), false);
    size_t required_remaining = 0;
    for (const auto& s : sites()) if (s.required) ++required_remaining;
    const auto start = GetTickCount64();
    while (!stop.stop_requested() && required_remaining && GetTickCount64() - start < timeout_ms) {
        for (size_t i = 0; i < sites().size(); ++i) {
            if (done[i]) continue;
            if (patch_one(process, image, sites()[i])) {
                done[i] = true;
                if (sites()[i].required) --required_remaining;
            }
        }
        if (WaitForSingleObject(process, 0) == WAIT_OBJECT_0) break;
        // One-time diagnostic per required site at ~60s if still unpatched, to
        // record whether the code is resident/relocated without ending polling.
        if (GetTickCount64() - start > 60000)
            for (size_t i = 0; i < sites().size(); ++i)
                if (!done[i] && sites()[i].required && !diagnosed[i]) { diagnose(process, image, sites()[i]); diagnosed[i] = true; }
        Sleep(200);
    }
    if (!required_remaining)
        std::cout << "bgs TLS patch: required candidate sites patched; handshake acceptance still requires server-side verification." << std::endl;
    else if (stop.stop_requested() || WaitForSingleObject(process, 0) == WAIT_OBJECT_0)
        std::cout << "bgs TLS patch: diagnostic ended with required sites unpatched." << std::endl;
    else
        std::cout << "bgs TLS patch: gave up after timeout with required sites unpatched." << std::endl;
}

} // namespace retail_tls_patch
