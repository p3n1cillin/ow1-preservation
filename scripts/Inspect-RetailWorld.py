"""Read-only fingerprinted final-OW1 world state inspection in a local dump.

Checks captured native instructions, vtables and owner decoding before reporting
state. The requested-map field is a descriptor pointer, NOT a resource GUID.
No live-process writes, injection, resource extraction or authentication calls.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

spec = importlib.util.spec_from_file_location('dump_reader', Path(__file__).with_name('Inspect-StartupDump.py'))
dump_reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(dump_reader)

EXE_SHA256 = 'ef67d348ecca066ce1698683fd0fd810075357164b345d83ed9296d676e0ebe2'
IMAGE_BYTES = 58298368
TIMESTAMP = 1661534873
WORLD_VTABLE = 0x2655d88
SECONDARY_VTABLE = 0x2618220
OWNER_VTABLE = 0x260be40
OWNER_OPERAND = 0x2ee48a1
OWNER_XOR_CONSTANT = 0x4dfd564467c27b96
# Only short instruction guards are retained; captured image bytes stay local.
GUARDS = {
    0xb4a5c2: bytes.fromhex('488d05bfb7b001488903'),  # constructor binds world vtable
    0xb4b5cd: bytes.fromhex('c6411802'),               # initializer sets state 2
    0xb4cca8: bytes.fromhex('0fb64318'),               # tick reads state at +18
    0xb52b88: bytes.fromhex('488b79204885ff'),          # idle reads request POINTER
    0xb52bc3: bytes.fromhex('8b07'),                   # dereferences descriptor index
    0xb4cd59: bytes.fromhex('488b05417b390248b9967bc2674456fd4d'),
}


def verify_image(image, base):
    if len(image) != IMAGE_BYTES: raise ValueError('Unexpected final image size')
    for rva, expected in GUARDS.items():
        if image[rva:rva + len(expected)] != expected: raise ValueError(f'Native instruction guard differs at {rva:x}')
    for slot, function in [(0, 0xb4a860), (5, 0xb4a7d0), (6, 0xb4b5c0), (14, 0xb4b5f0)]:
        if struct.unpack_from('<Q', image, WORLD_VTABLE + slot * 8)[0] != base + function:
            raise ValueError('World vtable slot differs')
    table = struct.unpack_from('<8I', image, 0xb4d8e4)
    if table != (0xb4ccca, 0xb4ccd4, 0xb4cce7, 0xb4ccf1, 0xb4ccfb, 0xb4cd05, 0xb4cd20, 0xb4cd0f):
        raise ValueError('Native state dispatch differs')


def world_state(reader, address, image, base):
    blob = reader.memory(address, 0x48)
    vft, encoded_owner, secondary = struct.unpack_from('<3Q', blob)
    if vft != base + WORLD_VTABLE or secondary != base + SECONDARY_VTABLE:
        raise ValueError('World object identities differ')
    operand = struct.unpack_from('<Q', image, OWNER_OPERAND)[0]
    owner = encoded_owner ^ operand ^ OWNER_XOR_CONSTANT
    if not 0 < owner < 0x800000000000 or owner % 8: raise ValueError('Decoded owner address bounds')
    if struct.unpack('<Q', reader.memory(owner, 8))[0] != base + OWNER_VTABLE:
        raise ValueError('World owner identity differs')
    state = blob[0x18]
    if state > 9: raise ValueError('Unknown native world state')
    request, load_timer, stall_timer = struct.unpack_from('<3Q', blob, 0x20)
    if request and (request >= 0x800000000000 or request % 8): raise ValueError('Request descriptor address bounds')
    request_index = struct.unpack('<I', reader.memory(request, 4))[0] if request else None
    return {'address': f'{address:x}', 'owner': f'{owner:x}', 'state': state,
            'request_descriptor_pointer': f'{request:x}', 'request_descriptor_first_u32': request_index,
            'load_timer': load_timer, 'stall_timer': stall_timer,
            'idle_without_request': state == 2 and request == 0}


def callback_metadata(reader, address, world):
    """Optional author-written FRP1 diagnostics; never infer these from game data."""
    if address % 4096: raise ValueError('Callback metadata allocation alignment')
    blob = reader.memory(address, 176)
    if blob[60:64] != b'FRP1' or blob[128:136] != bytes.fromhex('0107020007011b00'):
        raise ValueError('Callback metadata identity differs')
    begin, end, unwind = struct.unpack_from('<III', blob, 160)
    if begin != 256 or not begin < end < 2048 or unwind != 128:
        raise ValueError('Callback metadata code bounds')
    completion, entered = struct.unpack_from('<II', blob)
    if completion > 2 or entered > 10000 or blob[8] > 1:
        raise ValueError('Callback metadata submission bounds')
    native_request, index = struct.unpack_from('<QI', blob, 16)
    if completion == 2 and (not native_request or index != 0x688 or not blob[8]):
        raise ValueError('Callback metadata native ownership differs')
    active, native_index = struct.unpack_from('<I4xQ', blob, 96)
    if active > 1 or native_index >= 0x800000000000 or blob[56] not in (0, 1, 255):
        raise ValueError('Callback metadata native result bounds')
    return {'address': f'{address:x}', 'completion': completion, 'entered': entered,
            'native_request_submitted': completion == 2,
            'request_matches_world': native_request == int(world['request_descriptor_pointer'], 16),
            'loading_callbacks_returned': struct.unpack_from('<I', blob, 48)[0],
            'callback_active': bool(active), 'native_header_index_entry': f'{native_index:x}',
            'native_practice_header_available': None if blob[56] == 255 else bool(blob[56])}


def inspect(executable, dump_path):
    executable = Path(executable)
    if executable.stat().st_size != 52045144: raise ValueError('Unsupported executable size')
    with executable.open('rb') as source:
        if hashlib.file_digest(source, 'sha256').hexdigest() != EXE_SHA256:
            raise ValueError('Unsupported executable fingerprint')
    dump = dump_reader.Dump(dump_path)
    try:
        module = next((m for m in dump.modules if m['name'].lower().endswith('overwatch.exe')), None)
        if module is None or module['timestamp'] != TIMESTAMP or module['bytes'] != IMAGE_BYTES:
            raise ValueError('Captured module identity differs')
        image, base = dump.image(module), module['base']
        verify_image(image, base)
        if sum(size for _, size, _ in dump.regions) > 4 * 1024 * 1024 * 1024:
            raise ValueError('Captured-memory scan budget')
        pattern = struct.pack('<Q', base + WORLD_VTABLE)
        objects, rejected, callback_addresses = [], 0, set()
        for address, size, offset in dump.regions:
            for cursor in range(0, size, 8 * 1024 * 1024):
                block = dump.read(offset + cursor, min(size - cursor, 8 * 1024 * 1024 + 7))
                at = -1
                while (at := block.find(pattern, at + 1)) >= 0:
                    if at >= 8 * 1024 * 1024: continue  # next block handles overlap
                    candidate = address + cursor + at
                    if candidate % 8: continue
                    try: objects.append(world_state(dump, candidate, image, base))
                    except ValueError: rejected += 1
                    if len(objects) > 16: raise ValueError('Ambiguous world-object count')
                at = -1
                while (at := block.find(b'FRP1', at + 1)) >= 0:
                    if at >= 8 * 1024 * 1024: continue
                    candidate = address + cursor + at - 60
                    if candidate >= 0 and candidate % 4096 == 0: callback_addresses.add(candidate)
                    if len(callback_addresses) > 16: raise ValueError('Callback metadata candidate budget')
        if len(objects) != 1: raise ValueError(f'Requires one verified world object; found {len(objects)}')
        callbacks = []
        for address in sorted(callback_addresses):
            try: callbacks.append(callback_metadata(dump, address, objects[0]))
            except ValueError: pass  # An unrelated payload can contain the marker.
        if len(callbacks) > 1: raise ValueError('Ambiguous callback metadata')
        return {'build': '1.74.0.0.104319', 'read_only': True, 'native_instruction_guards_verified': True,
                'captured_module': module, 'world': objects[0], 'rejected_pointer_candidates': rejected,
                'probe_callback_metadata': callbacks[0] if callbacks else None,
                'scope': 'Captured world/owner identity and state only; map/session/controller initialization unverified.'}
    finally: dump.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable'); parser.add_argument('dump')
    args = parser.parse_args()
    print(json.dumps(inspect(args.executable, args.dump), indent=2))
