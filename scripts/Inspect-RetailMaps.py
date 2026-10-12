"""Hash-verify and inspect previously audited bundled final-OW1 map headers.

Reads original CASC offline. Prints metadata only; does not load a game map.
Supply the external audit folder created by Inspect-RetailStorage.py.
"""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
from retail_stu import StructuredData

spec = importlib.util.spec_from_file_location('retail', Path(__file__).with_name('Inspect-RetailStorage.py'))
retail = importlib.util.module_from_spec(spec); spec.loader.exec_module(retail)


def inspect(folder, dll, audit, selected=()):
    audit = Path(audit)
    report = json.loads((audit / 'report.json').read_text(encoding='utf8'))
    if report['build'] != '1.74.0.0.104319': raise ValueError('Requires final retail audit')
    with (audit / 'base-assets.tsv').open() as source:
        records = {r['guid']:r for r in csv.DictReader(source, delimiter='\t')}
    if len(selected) > 8 or any(len(g) != 16 or g not in records or not g.startswith('0800') for g in selected):
        raise ValueError('Select at most eight exact map-root GUIDs from the base manifest')
    grouped = {}
    for item in report['map_headers_hash_verified']:
        grouped.setdefault(item['bundle_guid'], []).append(item)
    storage = retail.packages.Storage(folder, dll)
    try:
        maps = []
        for bundle_guid, items in grouped.items():
            record = records[bundle_guid]
            key = bytes.fromhex(record['content_md5']); blob = storage.read(key, True)
            retail.packages.checked_hash(blob, key)
            if len(blob) != int(record['bytes']): raise ValueError('Bundle size differs')
            table_end, entries = retail.bundle_entries(blob)
            for item in items:
                record = records[item['guid']]; size = int(record['bytes'])
                offset = entries[int(item['guid'], 16)]
                if offset < table_end or offset + size > len(blob): raise ValueError('Map slice bounds')
                data = blob[offset:offset + size]
                retail.packages.checked_hash(data, bytes.fromhex(record['content_md5']))
                parsed = StructuredData(data).map_header()
                parsed.update(header_guid=item['guid'], content_md5=record['content_md5'])
                parsed['map_reference_in_base_manifest'] = parsed['map_guid'] in records
                maps.append(parsed)
        checks, failures = {}, []

        def check_map_root(guid, data, source):
            record = records[guid]
            retail.packages.checked_hash(data, bytes.fromhex(record['content_md5']))
            if len(data) != int(record['bytes']): raise ValueError('Map root size differs')
            checks[guid] = {'guid': guid, 'source': source, 'bytes': len(data),
                            'content_md5': record['content_md5'], 'format': 'Unparsed map-root resource'}

        for guid in selected:
            try: check_map_root(guid, storage.read(bytes.fromhex(records[guid]['content_md5']), True), 'direct')
            except (OSError, ValueError): pass  # Direct absence alone does not establish missing data.
        bundles_read, bytes_read = 0, 0
        for bundle_guid, record in sorted(records.items(), key=lambda row: int(row[1]['bytes'])):
            wanted = set(selected) - checks.keys()
            if not wanted: break
            if int(bundle_guid, 16) & 0xfff000000000000 != 0xd90000000000000: continue
            size = int(record['bytes'])
            if bundles_read >= 256 or bytes_read + size > 512 * 1024 * 1024:
                failures.append({'error': 'Bounded bundle-search budget reached'}); break
            bundles_read += 1; bytes_read += size
            try:
                key = bytes.fromhex(record['content_md5']); data = storage.read(key, True)
                retail.packages.checked_hash(data, key)
                if len(data) != size: raise ValueError('Bundle size differs')
                table_end, entries = retail.bundle_entries(data)
                for guid in wanted:
                    if int(guid, 16) not in entries: continue
                    offset = entries[int(guid, 16)]; asset_size = int(records[guid]['bytes'])
                    if offset < table_end or offset + asset_size > len(data): raise ValueError('Map root slice bounds')
                    check_map_root(guid, data[offset:offset + asset_size], bundle_guid)
            except (OSError, ValueError) as error: failures.append({'bundle_guid': bundle_guid, 'error': str(error)})
        return {'build': report['build'], 'offline': True,
                'scope': 'Audited map headers and selected map-root payloads only; native loading/dependencies unverified.',
                'maps': maps, 'map_roots_hash_verified': list(checks.values()),
                'unresolved_map_roots': sorted(set(selected) - checks.keys()),
                'map_root_search_bundles': bundles_read, 'map_root_search_bytes': bytes_read,
                'map_root_search_failures': failures}
    finally: storage.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder'); parser.add_argument('--casclib', required=True); parser.add_argument('--audit', required=True)
    parser.add_argument('--map-guid', action='append', default=[], help='Optional exact map-root GUID; maximum eight')
    args = parser.parse_args()
    print(json.dumps(inspect(args.folder, args.casclib, args.audit, args.map_guid), indent=2))
