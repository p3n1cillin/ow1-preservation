"""Read virtual addresses out of a Windows minidump and disassemble on demand.

Analysis helper for the OW1 preservation server: the retail client is packed on
disk, so static RE uses the decrypted in-memory image captured in a full-memory
minidump (see memory/re-tooling). This module parses the Memory64 list and maps
VA -> file offset; it holds no client bytes itself. Run isolated:

    PYTHONPATH=<scratch>/pylibs python -I tools/offline-launch/re/mdump.py <dump> <cmd> ...

Commands: find <ascii>        locate a string and its referencing code
          dis <hexVA> [n]     disassemble n instructions at a VA
"""
import struct, sys

IMAGE_BASE = 0x7ff794400000


class Dump:
    def __init__(self, path):
        self.f = open(path, "rb")
        data = self.f.read(0x1000)
        assert data[:4] == b"MDMP", "not a minidump"
        nstreams, dir_rva = struct.unpack_from("<II", data, 8)
        self.ranges = []  # (va_start, size, file_offset)
        self.f.seek(dir_rva)
        directory = self.f.read(nstreams * 12)
        for i in range(nstreams):
            stype, dsize, rva = struct.unpack_from("<III", directory, i * 12)
            if stype == 9:  # Memory64ListStream
                self.f.seek(rva)
                nranges, base_rva = struct.unpack("<QQ", self.f.read(16))
                descs = self.f.read(nranges * 16)
                off = base_rva
                for j in range(nranges):
                    va, size = struct.unpack_from("<QQ", descs, j * 16)
                    self.ranges.append((va, size, off))
                    off += size
        self.ranges.sort()

    def read(self, va, n):
        out = bytearray()
        while n > 0:
            for start, size, off in self.ranges:
                if start <= va < start + size:
                    take = min(n, start + size - va)
                    self.f.seek(off + (va - start))
                    out += self.f.read(take)
                    va += take; n -= take
                    break
            else:
                break
        return bytes(out)

    def find_all(self, needle):
        """Yield every VA whose mapped bytes start with needle."""
        for start, size, off in self.ranges:
            self.f.seek(off)
            buf = self.f.read(size)
            i = buf.find(needle)
            while i >= 0:
                yield start + i
                i = buf.find(needle, i + 1)

    def xrefs(self, target_va, limit=60):
        """RIP-relative lea/mov disp32 references to target_va (numpy-vectorized).
        Matches 48/4C 8D|8B modrm disp32 where start+i+7+disp == target_va."""
        import numpy as np
        hits = []
        for start, size, off in self.ranges:
            if size > 400 << 20:  # skip the giant data heaps
                continue
            self.f.seek(off)
            a = np.frombuffer(self.f.read(size), dtype=np.uint8)
            if a.size < 8:
                continue
            op = ((a[:-7] == 0x48) | (a[:-7] == 0x4C)) & ((a[1:-6] == 0x8D) | (a[1:-6] == 0x8B))
            idx = np.nonzero(op)[0]
            if idx.size == 0:
                continue
            disp = (a[idx + 3].astype(np.int64) | (a[idx + 4].astype(np.int64) << 8)
                    | (a[idx + 5].astype(np.int64) << 16) | (a[idx + 6].astype(np.int64) << 24))
            disp = disp.astype(np.int32).astype(np.int64)  # sign-extend disp32
            want = target_va - (start + 7) - idx.astype(np.int64)
            for i in idx[disp == want]:
                hits.append(start + int(i))
                if len(hits) >= limit:
                    return hits
        return hits


def disasm(dump, va, count=40):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    code = dump.read(va, count * 15)
    for ins in md.disasm(code, va):
        print(f"  {ins.address:012x}  {ins.mnemonic:<7} {ins.op_str}")
        count -= 1
        if count <= 0:
            break


def main():
    dump = Dump(sys.argv[1]); cmd = sys.argv[2]
    if cmd == "find":
        needle = sys.argv[3].encode()
        for va in dump.find_all(needle):
            print(f"string {needle!r} @ {va:012x} (rva {va - IMAGE_BASE:08x})", flush=True)
            for ref in dump.xrefs(va):
                print(f"  xref @ {ref:012x} (rva {ref - IMAGE_BASE:08x})", flush=True)
    elif cmd == "dis":
        va = int(sys.argv[3], 16)
        if va < IMAGE_BASE:
            va += IMAGE_BASE
        disasm(dump, va, int(sys.argv[4]) if len(sys.argv) > 4 else 40)


if __name__ == "__main__":
    main()
