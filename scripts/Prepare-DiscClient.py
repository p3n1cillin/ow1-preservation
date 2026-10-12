"""Recover verified install-manifest files from the supplied disc, without executing them.

This is a diagnostic staging folder, not a complete installed CASC client.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

spec = importlib.util.spec_from_file_location('disc', Path(__file__).with_name('Inspect-Disc.py'))
disc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(disc_module)


def records(disc):
    index = disc.file('data/0000')
    if hashlib.md5(index).hexdigest() != '4382d23c457d836f51152703112cccaf':
        raise ValueError('This staging tool requires the inspected disc index')
    for group in range(3):
        number, offset, length = struct.unpack('>HII', index[10 + group * 10:20 + group * 10])
        archive = 'data/' + format(number, '04x')
        base, archive_size, _, _ = disc.files[archive]
        for cursor in range(offset, offset + length, 24):
            entry = index[cursor:cursor + 24]
            position, size = struct.unpack('>II', entry[16:])
            if position + size > archive_size:
                raise ValueError('Disc archive bounds')
            yield entry[:16].hex(), base + position, size


def prepare(iso, destination):
    destination = Path(destination).resolve()
    repo = Path(__file__).resolve().parents[1]
    if destination == repo or repo in destination.parents:
        raise ValueError('Proprietary client must stay outside the source repository')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Use a new empty staging folder; existing files are not overwritten')
    disc = disc_module.Disc(iso)
    try:
        all_records = list(records(disc))
        install_record = next((entry for entry in all_records if entry[0] == 'eed90f42128bdcb38a2b593bd36adac7'), None)
        if not install_record:
            raise ValueError('Expected install manifest missing')
        manifest = disc_module.install_entries(disc_module.decode_blte(disc.read(install_record[1], install_record[2])))
        wanted = {entry['content_md5']: entry for entry in manifest}
        recovered = {}
        destination.mkdir(parents=True, exist_ok=True)
        for key, offset, size in all_records:
            header = disc.read(offset, min(size, 12))
            if header[:4] != b'BLTE':
                continue
            header_size = int.from_bytes(header[4:8], 'big')
            chunk_offset = header_size if header_size else 8
            if chunk_offset >= size or disc.read(offset + chunk_offset, 1) not in (b'N', b'Z'):
                continue
            if size > 64 * 1024 * 1024:
                continue
            payload = disc_module.decode_blte(disc.read(offset, size))
            content = hashlib.md5(payload).hexdigest()
            if content not in wanted:
                continue
            entry = wanted[content]
            if len(payload) != entry['bytes']:
                raise ValueError('Install-manifest size mismatch')
            target = (destination / entry['name']).resolve()
            if destination not in target.parents:
                raise ValueError('Unsafe install path')
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(payload)
            recovered[entry['name']] = {'bytes':len(payload), 'sha256':hashlib.sha256(payload).hexdigest(), 'encoded_key':key}
            if len(recovered) == len(manifest):
                break
        missing = [entry['name'] for entry in manifest if entry['name'] not in recovered]
        report = {'client_fixed_version':'1.0.1.27578', 'destination':str(destination),
                  'recovered':recovered, 'missing_install_files':missing,
                  'complete_casc_installation':False}
        (destination / 'staging-report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        if missing:
            raise ValueError('Missing installation files: ' + ', '.join(missing))
        print(json.dumps(report, indent=2))
    finally:
        disc.stream.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso')
    parser.add_argument('destination')
    args = parser.parse_args()
    prepare(args.iso, args.destination)
