"""Synthetic decoder checks; requires the separately built manifest probe."""
import argparse
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile


def run(probe):
    with tempfile.TemporaryDirectory(prefix='ow1-manifest-test-') as folder:
        root = Path(folder).resolve()
        if root.parent != Path(tempfile.gettempdir()).resolve(): raise ValueError('Temporary fixture bounds')
        source = root / 'Win_SPWin_RDEV_EExt.cmf'
        data = bytearray(97)
        struct.pack_into('<I', data, 0, 104319)
        struct.pack_into('<I', data, 32, 1)
        struct.pack_into('<I', data, 40, 1)
        struct.pack_into('<I', data, 44, 0x1b666d63)
        struct.pack_into('<IQQ', data, 48, 1, 2, 3)
        struct.pack_into('<QIB16s', data, 68, 0x0790000000000001, 5, 0, hashlib.md5(b'asset').digest())

        def invoke(blob, output, digest=None):
            source.write_bytes(blob)
            return subprocess.run(['dotnet', str(probe), str(source), digest or hashlib.md5(blob).hexdigest(), str(output)],
                                  capture_output=True, text=True)

        output = root / 'records.tsv'
        result = invoke(data, output)
        if result.returncode or len(output.read_text().splitlines()) != 2: raise AssertionError(result.stderr)
        before = output.read_bytes()
        if invoke(data, output).returncode == 0 or output.read_bytes() != before: raise AssertionError('Existing output overwritten')
        malformed = []
        oversized = bytearray(data); struct.pack_into('<I', oversized, 32, 2000001); malformed.append(oversized)
        bad_iv = bytearray(data); struct.pack_into('<I', bad_iv, 48, 99); malformed.append(bad_iv)
        bad_build = bytearray(data); struct.pack_into('<I', bad_build, 0, 27578); malformed.append(bad_build)
        malformed.extend([data[:47], data[:-1]])
        for n, blob in enumerate(malformed):
            target = root / f'invalid-{n}.tsv'
            if invoke(blob, target).returncode == 0 or target.exists(): raise AssertionError('Malformed manifest accepted')
        target = root / 'wrong-hash.tsv'
        if invoke(data, target, '00' * 16).returncode == 0 or target.exists(): raise AssertionError('Wrong MD5 accepted')
        print('PASS: valid fixture, existing output, wrong hash/build, truncation, counts and decoded-entry checks')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('probe', type=Path)
    run(parser.parse_args().probe.resolve())
