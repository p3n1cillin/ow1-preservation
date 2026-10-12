"""Read-only 27578 package/asset checks with an independently built CascLib.

No extraction or online flags. Old APM/package layout identified from local
captures and CascLib's MIT-licensed format definitions (see DISC_RUNTIME.md).
"""
import argparse
import ctypes
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct


class Storage:
    def __init__(self, folder, dll):
        self.lib = ctypes.WinDLL(str(Path(dll).resolve()), use_last_error=True)
        handle = ctypes.c_void_p
        definitions = {
            'CascOpenStorage': [ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(handle)],
            'CascOpenFile': [handle, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(handle)],
            'CascGetFileSize64': [handle, ctypes.POINTER(ctypes.c_uint64)],
            'CascReadFile': [handle, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)],
            'CascCloseFile': [handle], 'CascCloseStorage': [handle]}
        for name, args in definitions.items():
            function = getattr(self.lib, name)
            function.argtypes = args; function.restype = ctypes.c_bool
        self.handle = handle()
        self.check(self.lib.CascOpenStorage(str(Path(folder).resolve()).encode('mbcs'), 2, ctypes.byref(self.handle)))

    @staticmethod
    def check(result):
        if not result: raise OSError(ctypes.get_last_error(), 'Offline CASC read failed')

    def read(self, name, key=False):
        file = ctypes.c_void_p()
        self.check(self.lib.CascOpenFile(self.handle, name, 2, int(key), ctypes.byref(file)))
        try:
            length = ctypes.c_uint64()
            self.check(self.lib.CascGetFileSize64(file, ctypes.byref(length)))
            if length.value > 128 * 1024 * 1024: raise ValueError('Asset size limit')
            buffer = ctypes.create_string_buffer(length.value); count = ctypes.c_uint32()
            self.check(self.lib.CascReadFile(file, buffer, length.value, ctypes.byref(count)))
            if count.value != length.value: raise ValueError('Incomplete asset read')
            return buffer.raw
        finally:
            self.lib.CascCloseFile(file)

    def contains(self, key):
        file = ctypes.c_void_p()
        if not self.lib.CascOpenFile(self.handle, key, 2, 1, ctypes.byref(file)): return False
        try:
            length = ctypes.c_uint64()
            return bool(self.lib.CascGetFileSize64(file, ctypes.byref(length)))
        finally:
            self.lib.CascCloseFile(file)

    def close(self):
        self.lib.CascCloseStorage(self.handle)


def apm_packages(data):
    if len(data) < 24: raise ValueError('Truncated APM header')
    _, build, packages, entries, magic = struct.unpack_from('<QIIII', data)
    if build != 27578 or magic != 0x13636d66: raise ValueError('Requires disc 27578 APM')
    if packages > 10000 or entries > 4096: raise ValueError('APM count limit')
    offset = 24 + entries * 12
    if offset + packages * 72 != len(data): raise ValueError('APM bounds')
    result = {}
    for cursor in range(offset, len(data), 72):
        _, guid, _, _, package, _, _, _, key = struct.unpack_from('<QQQQQIIQ16s', data, cursor)
        if package in result: raise ValueError('Duplicate package identity')
        result[package] = {'guid':guid, 'key':key}
    return result


def package_records(data):
    if len(data) < 96: raise ValueError('Truncated package header')
    begin, end, auxiliary, reserved = struct.unpack_from('<4Q', data)
    version, count = struct.unpack_from('<II', data, 32)
    compressed = struct.unpack_from('<Q', data, 40)[0]
    bundles = struct.unpack_from('<I', data, 48)[0]
    if version not in (1, *range(20, 28)) or reserved or begin != 96 or auxiliary != end:
        raise ValueError('Unsupported package layout')
    if count > 100000 or bundles > 4096 or end != begin + compressed or end + bundles * 4 != len(data):
        raise ValueError('Package bounds')
    with gzip.GzipFile(fileobj=io.BytesIO(data[begin:end])) as stream:
        records = stream.read(count * 36 + 1)
    if len(records) != count * 36: raise ValueError('Package record count mismatch')
    dependencies = struct.unpack_from('<' + 'I' * bundles, data, end)
    content_bytes = struct.unpack_from('<Q', data, 64)[0]
    return {'records':[struct.unpack_from('<QIII16s', records, p) for p in range(0, len(records), 36)],
            'dependencies':dependencies, 'content_key':data[76:92], 'content_bytes':content_bytes}


def checked_hash(blob, key):
    if hashlib.md5(blob).digest() != key: raise ValueError('Content hash mismatch')


def inspect(folder, dll, map_id, verify_assets=False, include_localized=False):
    storage = Storage(folder, dll)
    try:
        apm = storage.read(b'Manifest/Win_SPWin_RDEV_LenUS_EExt.apm')
        checked_hash(apm, bytes.fromhex('1c03e74827ec7e42781f83bb8a1c5683'))
        packages = apm_packages(apm)
        if include_localized:
            speech = storage.read(b'Manifest/Win_SPWin_speech_RDEV_LenUS_EExt.apm')
            checked_hash(speech, bytes.fromhex('9f8caf03d04d9c85292cf420bd3c341e'))
            speech_packages = apm_packages(speech)
            if packages.keys() & speech_packages.keys(): raise ValueError('Overlapping speech identities')
            packages.update(speech_packages)
        matching = [p for p, row in packages.items() if row['guid'] == map_id and not p & 0x300000000000]
        if len(matching) != 1: raise ValueError('Map package missing or ambiguous')
        pending = list(matching); seen = set(); results = []; failures = []; verified_keys = {}
        while pending:
            identity = pending.pop()
            if identity in seen: continue
            seen.add(identity)
            if len(seen) > len(packages): raise ValueError('Dependency graph limit')
            row = packages.get(identity)
            if row is None:
                failures.append({'package':hex(identity), 'error':'APM entry missing'}); continue
            if include_localized and not identity & 0x300000000000:
                pending.extend(identity | variant for variant in (0x100000000000, 0x200000000000)
                               if identity | variant in packages)
            blob = storage.read(row['key'], True); checked_hash(blob, row['key'])
            package = package_records(blob)
            # A package containing only loose files can have no content block.
            if not package['content_bytes'] and package['content_key'] == bytes(16):
                content = b''
            else:
                try:
                    content = storage.read(package['content_key'], True)
                    checked_hash(content, package['content_key'])
                except OSError as error:
                    content = None
                    failures.append({'package':hex(identity), 'key':package['content_key'].hex(),
                                     'kind':'content_block', 'bytes':package['content_bytes'], 'error':str(error)})
            if content is not None and len(content) != package['content_bytes']: raise ValueError('Content size mismatch')
            bundled = available = verified = 0
            for guid, size, flags, offset, key in package['records']:
                if flags & 0x40000000:
                    if content is None: continue
                    if offset + size > len(content): raise ValueError('Bundled asset bounds')
                    checked_hash(content[offset:offset + size], key); bundled += 1
                elif verify_assets:
                    try:
                        if key not in verified_keys:
                            asset = storage.read(key, True); checked_hash(asset, key)
                            verified_keys[key] = len(asset)
                        if verified_keys[key] != size: raise ValueError('Loose asset size mismatch')
                        available += 1; verified += 1
                    except OSError as error:
                        failures.append({'guid':hex(guid), 'key':key.hex(), 'error':str(error)})
                elif storage.contains(key): available += 1
                else: failures.append({'guid':hex(guid), 'key':key.hex(), 'error':'Loose asset unavailable'})
            results.append({'package':hex(identity), 'resource':hex(row['guid']), 'records':len(package['records']),
                            'bundled_assets_hash_verified':bundled, 'loose_assets_available':available,
                            'loose_assets_hash_verified':verified, 'content_bytes':package['content_bytes'],
                            'content_available':content is not None})
            pending.extend(0x06e0000000000000 | number for number in package['dependencies'])
        return {'map':hex(map_id), 'offline':True, 'localized_variants_checked':include_localized,
                'packages':results, 'failures':failures,
                'native_map_rendering_verified':False}
    finally:
        storage.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder'); parser.add_argument('--casclib', required=True)
    parser.add_argument('--map', type=lambda value:int(value, 16), default=0x0800000000000165)
    parser.add_argument('--verify-assets', action='store_true')
    parser.add_argument('--include-localized', action='store_true', help='Also check English text/speech package variants')
    args = parser.parse_args()
    report = inspect(args.folder, args.casclib, args.map, args.verify_assets, args.include_localized)
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report['failures'] else 0)
