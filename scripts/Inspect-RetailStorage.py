"""Read-only final-OW1 metadata, direct-index and bundled map-header checks.

Requires an external CascLib DLL and the source-built final-manifest-probe.
Only metadata copies/TSVs/reports are written, to a new folder outside Git.
Bundle layout reference: TACTLib 388f8dd Bundle.cs (MIT). Neither unmatched
logical CKeys nor an unavailable decryption key prove missing physical files.
"""
import argparse
import csv
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess

spec = importlib.util.spec_from_file_location('packages', Path(__file__).with_name('Inspect-DiscPackages.py'))
packages = importlib.util.module_from_spec(spec); spec.loader.exec_module(packages)
BUILD_CONFIG = '786a31729ba1c684a5c80fbaf7cb92b8'


class FindData(ctypes.Structure):
    _fields_ = [('name', ctypes.c_char * 260), ('ckey', ctypes.c_ubyte * 16), ('ekey', ctypes.c_ubyte * 16),
                ('tags', ctypes.c_uint64), ('size', ctypes.c_uint64), ('plain', ctypes.c_void_p),
                ('id', ctypes.c_uint32), ('locale', ctypes.c_uint32), ('flags', ctypes.c_uint32),
                ('spans', ctypes.c_uint32), ('available', ctypes.c_uint32), ('name_type', ctypes.c_uint32)]


def local_keys(storage):
    lib = storage.lib
    lib.CascFindFirstFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(FindData), ctypes.c_char_p]
    lib.CascFindFirstFile.restype = ctypes.c_void_p
    lib.CascFindNextFile.argtypes = [ctypes.c_void_p, ctypes.POINTER(FindData)]; lib.CascFindNextFile.restype = ctypes.c_bool
    lib.CascFindClose.argtypes = [ctypes.c_void_p]; lib.CascFindClose.restype = ctypes.c_bool
    data = FindData(); find = lib.CascFindFirstFile(storage.handle, b'*', ctypes.byref(data), None)
    if not find or find == ctypes.c_void_p(-1).value: raise OSError('Offline index enumeration failed')
    keys = set(); count = 0
    try:
        while True:
            count += 1
            if count > 2000000: raise ValueError('Enumeration limit')
            if data.available & 1: keys.add(bytes(data.ckey).hex())
            if not lib.CascFindNextFile(find, ctypes.byref(data)): break
        return keys, count
    finally: lib.CascFindClose(find)


def bundle_entries(blob):
    if len(blob) < 5: raise ValueError('Truncated bundle header')
    count, width = struct.unpack_from('<iB', blob)
    if not 0 <= count <= 1000000 or width not in (1, 2, 4): raise ValueError('Bundle count/offset width')
    end = 5 + count * (8 + width)
    if end > len(blob): raise ValueError('Bundle table bounds')
    entries = {}
    for n in range(count):
        at = 5 + n * (8 + width); guid = struct.unpack_from('<Q', blob, at)[0]
        if guid in entries: raise ValueError('Duplicate bundle GUID')
        entries[guid] = int.from_bytes(blob[at + 8:at + 8 + width], 'little')
    return end, entries


def inspect(folder, dll, probe, output):
    folder, output = Path(folder).resolve(), Path(output).resolve()
    repo = Path(__file__).resolve().parents[1]
    if output == repo or repo in output.parents: raise ValueError('Metadata/payload artifacts must stay outside Git')
    if output.exists(): raise ValueError('Use a new output folder; existing output is preserved')
    config = folder / 'data/casc/config' / BUILD_CONFIG[:2] / BUILD_CONFIG[2:4] / BUILD_CONFIG
    blob = config.read_bytes(); packages.checked_hash(blob, bytes.fromhex(BUILD_CONFIG))
    values = dict(line.split(' = ', 1) for line in blob.decode('ascii').splitlines() if ' = ' in line)
    if values.get('build-name') != 'prometheus-1_74_0_0-104319': raise ValueError('Unexpected final build config')
    output.mkdir(parents=True)
    storage = packages.Storage(folder, dll)
    try:
        root_key = bytes.fromhex(values['root'].split()[0]); root = storage.read(root_key, True)
        packages.checked_hash(root, root_key)
        root_rows = [line.split('|') for line in root.decode('ascii').splitlines()[1:]]
        report = {'build':'1.74.0.0.104319', 'offline':True, 'build_config_hash_verified':BUILD_CONFIG,
                  'root_hash_verified':root_key.hex(), 'named_root_entries':len(root_rows), 'manifests':[]}
        local, total = local_keys(storage)
        report.update(enumerated_files=total, local_content_keys=len(local))
        base = None
        for role, name in [('base','Win_SPWin_RDEV_EExt.cmf'), ('text-enUS','Win_SPWin_RDEV_LenUS_text_EExt.cmf'),
                           ('speech-enUS','Win_SPWin_RDEV_LenUS_speech_EExt.cmf')]:
            row = next(r for r in root_rows if r[5] == 'TactManifest/' + name)
            data = storage.read(('TactManifest/' + name).encode('ascii')); packages.checked_hash(data, bytes.fromhex(row[1]))
            path = output / name; path.write_bytes(data); records_path = output / (role + '-assets.tsv')
            result = subprocess.run(['dotnet', str(Path(probe).resolve()), str(path), row[1], str(records_path)],
                                    capture_output=True, text=True)
            if result.returncode: raise ValueError('Manifest decoder rejected input: ' + result.stderr.strip())
            with records_path.open() as source: rows = list(csv.DictReader(source, delimiter='\t'))
            present = sum(r['content_md5'] in local for r in rows)
            report['manifests'].append({'role':role, 'bytes':len(data), 'content_md5':row[1].lower(),
                                       **json.loads(result.stdout), 'direct_local_index_matches':present,
                                       'without_direct_local_index_match':len(rows) - present})
            if role == 'base': base = rows
        by_guid = {int(row['guid'], 16):row for row in base}
        wanted = {g for g in by_guid if int(f'{(g >> 48) & 0xfff:012b}'[::-1], 2) + 1 == 0x9f}
        report['map_header_records'] = len(wanted)
        report['map_headers_hash_verified'] = []; report['bundle_failures'] = []; checked = 0
        for guid, row in by_guid.items():
            if guid & 0xfff000000000000 != 0xd90000000000000: continue
            try:
                key = bytes.fromhex(row['content_md5']); data = storage.read(key, True); packages.checked_hash(data, key)
                if len(data) != int(row['bytes']): raise ValueError('Bundle size mismatch')
                table_end, entries = bundle_entries(data); checked += 1
                for asset_guid in wanted.intersection(entries):
                    asset = by_guid[asset_guid]; offset = entries[asset_guid]; size = int(asset['bytes'])
                    if offset < table_end or offset + size > len(data): raise ValueError('Bundled map bounds')
                    packages.checked_hash(data[offset:offset + size], bytes.fromhex(asset['content_md5']))
                    report['map_headers_hash_verified'].append({'guid':asset['guid'], 'content_md5':asset['content_md5'],
                                                               'bytes':size, 'bundle_guid':row['guid']})
                    wanted.remove(asset_guid)
            except (OSError, ValueError) as error: report['bundle_failures'].append({'guid':row['guid'], 'error':str(error)})
            if len(report['map_headers_hash_verified']) >= 12: break
        report.update(bundles_hash_verified=checked, all_bundles_checked=False,
                      scope='Direct-index matches plus a bounded bundled map-header sample; not a full asset-content or gameplay audit.')
        (output / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        return report
    finally: storage.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder'); parser.add_argument('--casclib', required=True)
    parser.add_argument('--manifest-probe', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = inspect(args.folder, args.casclib, args.manifest_probe, args.output)
    print(json.dumps({key:value for key,value in report.items() if key != 'map_headers_hash_verified'}, indent=2))
    print('map_headers_hash_verified:', len(report['map_headers_hash_verified']))
