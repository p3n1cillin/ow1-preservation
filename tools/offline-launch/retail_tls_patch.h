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
// locally configured --BNetServer connection is affected.
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

inline bool patch_one(HANDLE process, uint64_t image, const Site& site) {
    const auto anchor = image + site.anchor_rva;
    std::vector<unsigned char> window(site.signature.size());
    SIZE_T count = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<void*>(anchor), window.data(), window.size(), &count)
        || count != window.size() || memcmp(window.data(), site.signature.data(), window.size()))
        return false;
    const auto target = anchor + site.patch_offset;
    DWORD protect = 0, ignored = 0; SIZE_T written = 0;
    if (!VirtualProtectEx(process, reinterpret_cast<void*>(target), sizeof(patched), PAGE_EXECUTE_READWRITE, &protect))
        return false;
    const bool ok = WriteProcessMemory(process, reinterpret_cast<void*>(target), patched, sizeof(patched), &written)
        && written == sizeof(patched);
    VirtualProtectEx(process, reinterpret_cast<void*>(target), sizeof(patched), protect, &ignored);
    FlushInstructionCache(process, reinterpret_cast<void*>(target), sizeof(patched));
    if (ok) std::cout << "bgs TLS patch: '" << site.name << "' forced to accept at RVA 0x"
                      << std::hex << site.anchor_rva << std::dec << " (in-memory; disk unchanged)." << std::endl;
    return ok;
}

// Poll the child until each site's packed code has decrypted, then patch it.
// Does not throw; an interactive client is never torn down by a patch failure.
inline void apply(HANDLE process, uint64_t image, unsigned timeout_ms = 120000) {
    std::vector<bool> done(sites().size(), false);
    size_t remaining = sites().size();
    const auto start = GetTickCount64();
    while (remaining && GetTickCount64() - start < timeout_ms) {
        for (size_t i = 0; i < sites().size(); ++i) {
            if (done[i]) continue;
            if (patch_one(process, image, sites()[i])) { done[i] = true; --remaining; }
        }
        if (WaitForSingleObject(process, 0) == WAIT_OBJECT_0) break;
        if (remaining) Sleep(25);
    }
    for (size_t i = 0; i < sites().size(); ++i)
        if (!done[i] && sites()[i].required)
            std::cout << "bgs TLS patch: required site '" << sites()[i].name
                      << "' did not decrypt within timeout; handshake may still be rejected." << std::endl;
}

} // namespace retail_tls_patch
