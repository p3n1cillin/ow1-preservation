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
    0xb4ccd4: bytes.fromhex('833d6d6b7402007f43'),   # native state-3 gate
    0xb50053: bytes.fromhex('4883c118'),              # later loader examines request +18
    0xb510c3: bytes.fromhex('c647180a'),              # native terminal unload state 10
    0x684746: bytes.fromhex('488d0543cbf801488901'),  # native loading-context vtable
    0x6855ca: bytes.fromhex('488b050f318d02'),        # context service component root
    0x6855e3: bytes.fromhex('482b1de6f58502'),        # component array decoding operand
    0x60e6ef: bytes.fromhex('488bb958010000'),        # native metadata lookup count
    0x60e0bb: bytes.fromhex('488d05b6310002488901'),  # context service vtable
    0x60e0aa: bytes.fromhex('48b81a4c0e30a530b5f3'),  # decoded component owner identity
    0x821820: bytes.fromhex('833da1d1730200'),        # native async submission gate
    0x681ac3: bytes.fromhex('41c6866901000001'),      # queue-refusal terminal flag
    0x81c1e2: bytes.fromhex('66c741100d00'),          # internal metadata request kind 13
    0x81c1eb: bytes.fromhex('488d05d6c6df01'),        # original request object's vtable
    0x681909: bytes.fromhex('488d05304efd01'),        # original shared control block
    0x681ba3: bytes.fromhex('41807f11000f84b9010000'), # flag zero takes structured-error branch
    0x821bb7: bytes.fromhex('44387424300f94c0884711'), # worker stores error-status inversion
    0x81dcaf: bytes.fromhex('66c7070302'),            # metadata enumeration error status/domain
    0x81dc4f: bytes.fromhex('488d1502d4a502'),        # native Hotfix-directory string
    0x185d220: bytes.fromhex('ff5018'),              # directory provider's method dispatch
}


def verify_image(image, base):
    if len(image) != IMAGE_BYTES: raise ValueError('Unexpected final image size')
    for rva, expected in GUARDS.items():
        if image[rva:rva + len(expected)] != expected: raise ValueError(f'Native instruction guard differs at {rva:x}')
    for slot, function in [(0, 0xb4a860), (5, 0xb4a7d0), (6, 0xb4b5c0), (14, 0xb4b5f0)]:
        if struct.unpack_from('<Q', image, WORLD_VTABLE + slot * 8)[0] != base + function:
            raise ValueError('World vtable slot differs')
    if struct.unpack_from('<Q', image, 0x26188c8 + 8)[0] != base + 0x81dc30:
        raise ValueError('SDK directory-enumeration method differs')
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
    if state > 10: raise ValueError('Unknown native world state')
    request, load_timer, stall_timer = struct.unpack_from('<3Q', blob, 0x20)
    if request and (request >= 0x800000000000 or request % 8): raise ValueError('Request descriptor address bounds')
    descriptor = reader.memory(request, 0x38) if request else None
    request_index = struct.unpack_from('<I', descriptor)[0] if descriptor else None
    return {'address': f'{address:x}', 'owner': f'{owner:x}', 'state': state,
            'request_descriptor_pointer': f'{request:x}', 'request_descriptor_first_u32': request_index,
            # Zero is a native default identifier, not proof of an absent
            # context. Report only this byte predicate, never identifier bytes.
            'request_loading_context_nonzero': bool(any(descriptor[0x18:0x38])) if descriptor else None,
            'load_timer': load_timer, 'stall_timer': stall_timer,
            'idle_without_request': state == 2 and request == 0}


def loading_context_service(reader, image, base, context_pointer):
    """Bounded owner discovery; no context identifiers or payloads are returned."""
    root = struct.unpack_from('<Q', image, 0x2f586e0)[0]
    operand = struct.unpack_from('<Q', image, 0x2ee4bd0)[0]
    if not 0 < root < 0x800000000000 or root % 8: raise ValueError('Context component root bounds')
    encoded = struct.unpack('<Q', reader.memory(root + 0x140, 8))[0]
    array = encoded ^ ((0x4e3494c633194824 - operand) & 0xffffffffffffffff)
    if not 0 < array < 0x800000000000 or array % 8: raise ValueError('Context component array bounds')
    candidates = {}
    for slot, address in enumerate(struct.unpack('<256Q', reader.memory(array, 256 * 8))):
        if not 0 < address < 0x800000000000 or address % 8: continue
        try: blob = reader.memory(address, 0x1a8)
        except ValueError: continue
        vft, encoded_owner = struct.unpack_from('<2Q', blob)
        if vft != base + 0x2611278 or encoded_owner ^ 0xf3b530a5300e4c1a != root: continue
        previous, current = struct.unpack_from('<2Q', blob, 0x198)
        if context_pointer not in (previous, current): continue
        cached = struct.unpack_from('<Q', blob, 0x158)[0]
        subscribers = struct.unpack_from('<I', blob, 0xe8)[0]
        if cached > 4096 or subscribers > 4096: raise ValueError('Context service inspection budget')
        candidates[address] = {'address': f'{address:x}', 'component_slot': slot,
                               'current_context_matches': current == context_pointer,
                               'previous_context_matches': previous == context_pointer,
                               'cached_metadata_entries': cached,
                               'registered_context_change_subscribers': subscribers,
                               'metadata_initialization_terminal_flag_raw': blob[0x169],
                               'pending_metadata_action': f'{struct.unpack_from("<Q", blob, 0x118)[0]:x}',
                               'native_async_submission_gate_counter': struct.unpack_from('<i', image, 0x2f5e9c8)[0]}
    if len(candidates) != 1: raise ValueError('Requires one verified native context service')
    return next(iter(candidates.values()))


def callback_metadata(reader, address, world, image_base=None, image=None):
    """Optional author-written FRP1 diagnostics; never infer these from game data."""
    if address % 4096: raise ValueError('Callback metadata allocation alignment')
    blob = reader.memory(address, 256)
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
    resource_entry = struct.unpack_from('<Q', blob, 64)[0]
    if (active > 1 or native_index >= 0x800000000000 or resource_entry >= 0x800000000000
            or blob[56] not in (0, 1, 255) or blob[58] > 1 or blob[72] > 1 or blob[77] > 1):
        raise ValueError('Callback metadata native result bounds')
    update_observation = None
    if blob[77]:
        counters = struct.unpack_from('<3I', blob, 80)
        if any(state > 10 for state in blob[74:77]) or blob[78] not in (0, 1, 2) or any(count > 10000 for count in counters):
            raise ValueError('Callback metadata update observation bounds')
        update_observation = {'state_before': blob[74], 'state_after': blob[75],
                              'highest_returned_state': blob[76], 'maximum_updates_per_callback': blob[78] or None,
                              'calls_entered_from_loading_states': dict(zip(('2', '3', '4'), counters))}
    loading_context = None
    context_pointer = struct.unpack_from('<Q', blob, 176)[0]
    if context_pointer >= 0x800000000000 or any(flag > 1 for flag in blob[192:196]):
        raise ValueError('Callback loading-context metadata bounds')
    if not blob[192] and (context_pointer or blob[194] or blob[195]):
        raise ValueError('Callback loading-context constructor identity')
    if blob[194] and (not context_pointer or not blob[195]):
        raise ValueError('Callback loading-context activation identity')
    if blob[192]:
        loading_context = {'constructor_attempted': True, 'object_address': f'{context_pointer:x}',
                           'identity_verified': bool(blob[195]),
                           'activation_result': bool(blob[193]) if blob[194] else None,
                           'native_ready_flag_raw': None, 'native_reports_ready': None,
                           'native_service': None}
        if blob[195]:
            if image_base is None or not context_pointer or context_pointer % 8:
                raise ValueError('Context object verification requires captured image base and bounded pointer')
            context = reader.memory(context_pointer, 0xa0)
            if (struct.unpack_from('<Q', context)[0] != image_base + 0x2611290
                    or struct.unpack_from('<I', context, 0x10)[0] != 2
                    or not 0 < struct.unpack_from('<I', context, 8)[0] <= 1000000):
                raise ValueError('Native loading-context object identity differs')
            loading_context['native_ready_flag_raw'] = context[0x98]
            loading_context['native_reports_ready'] = bool(context[0x98])
            if image is not None:
                loading_context['native_service'] = loading_context_service(reader, image, image_base, context_pointer)
    metadata_handlers = None
    service_pointer, init_returns, process_returns = struct.unpack_from('<QII', blob, 208)
    if service_pointer >= 0x800000000000 or init_returns > 20000 or process_returns > 20000:
        raise ValueError('Metadata handler diagnostic bounds')
    if service_pointer:
        if (not loading_context or not loading_context['native_service']
                or int(loading_context['native_service']['address'], 16) != service_pointer):
            raise ValueError('Metadata handler service identity differs')
        metadata_handlers = {'initialization_handlers_returned': init_returns,
                             'processing_handlers_returned': process_returns}
    elif init_returns or process_returns:
        raise ValueError('Metadata handlers require verified service')
    sdk_request = None
    if any(flag > 1 for flag in blob[200:203]): raise ValueError('Retained SDK request flag bounds')
    control_pointer, action_pointer = struct.unpack_from('<2Q', blob, 240)
    if any(pointer >= 0x800000000000 for pointer in (control_pointer, action_pointer)):
        raise ValueError('Retained SDK request pointer bounds')
    if blob[202] and not blob[201]: raise ValueError('Retained SDK submission result requires a call')
    if blob[201] and not control_pointer: raise ValueError('Retained SDK submission requires an object')
    if blob[200]:
        sdk_request = {'allocation_attempted': True, 'submission_accepted': bool(blob[202]) if blob[201] else None,
                       'internal_kind': None, 'completed': None, 'queue_reset_marker_raw': None,
                       'result_flag_raw': None, 'result_succeeded': None, 'response_data_present': None,
                       'response_entry_count': None, 'error_status_raw': None,
                       'error_domain_raw': None, 'error_code_raw': None}
        gate_last, gate_first, gate_recorded = struct.unpack_from('<3I', blob, 224)
        if gate_recorded > 1: raise ValueError('Retained SDK submission gate observation bounds')
        sdk_request['submission_gate_before_call'] = gate_first if gate_recorded else None
        sdk_request['submission_gate_latest'] = gate_last if gate_recorded else None
        if image is not None:
            # Its input is a resident native path, not a service URL. Report
            # only the classification; never expose the user's full path.
            path = image[0x327b058:0x327b058 + 1024].split(b'\0', 1)[0]
            sdk_request['native_hotfix_directory_configured'] = path.lower().endswith(b'\\104319\\hotfix')
            sdk_request['operation'] = 'local_hotfix_directory_enumeration'
        if control_pointer:
            if image_base is None or control_pointer % 16 or action_pointer != control_pointer + 16:
                raise ValueError('Retained SDK request allocation identity')
            control = reader.memory(control_pointer, 16)
            vft, strong, weak = struct.unpack('<QII', control)
            action = reader.memory(action_pointer, 0x148)
            if (vft != image_base + 0x2656740 or not 0 < strong <= 1000000 or not 0 < weak <= 1000000
                    or struct.unpack_from('<Q', action)[0] != image_base + 0x26188c8 or action[0x10] != 13):
                raise ValueError('Retained SDK request native identity differs')
            if any(action[offset] > 1 for offset in (0x11, 0x130, 0x131)):
                raise ValueError('Retained SDK request native flag bounds')
            completed, succeeded = bool(action[0x130]), bool(action[0x11])
            sdk_request.update({'internal_kind': action[0x10], 'completed': bool(action[0x130]),
                                'queue_reset_marker_raw': action[0x131], 'result_flag_raw': action[0x11],
                                'result_succeeded': succeeded if completed else None,
                                'response_data_present': bool(struct.unpack_from('<Q', action, 0x138)[0])
                                                         if completed and succeeded else None,
                                'response_entry_count': struct.unpack_from('<i', action, 0x140)[0]
                                                        if completed and succeeded else None,
                                'error_status_raw': action[0x18] if completed and not succeeded else None,
                                'error_domain_raw': action[0x19] if completed and not succeeded else None,
                                'error_code_raw': struct.unpack_from('<q', action, 0x20)[0]
                                                  if completed and not succeeded else None})
    elif control_pointer or action_pointer or blob[201]:
        raise ValueError('Retained SDK request allocation attempt required')
    return {'address': f'{address:x}', 'completion': completion, 'entered': entered,
            'native_request_submitted': completion == 2,
            'request_matches_world': native_request == int(world['request_descriptor_pointer'], 16),
            'loading_callbacks_returned': struct.unpack_from('<I', blob, 48)[0],
            'callback_active': bool(active), 'native_header_index_entry': f'{native_index:x}',
            'native_practice_header_available': None if blob[56] == 255 else bool(blob[56]),
            'native_practice_header_load_state_raw': blob[57] if blob[58] else None,
            'native_header_resource_request_attempted': bool(blob[72]),
            'native_header_resource_request_entry': f'{resource_entry:x}',
            'native_update_observation': update_observation,
            'native_loading_context': loading_context,
            'native_metadata_handlers': metadata_handlers,
            'retained_sdk_metadata_request': sdk_request}


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
            try: callbacks.append(callback_metadata(dump, address, objects[0], base, image))
            except ValueError: pass  # An unrelated payload can contain the marker.
        if len(callbacks) > 1: raise ValueError('Ambiguous callback metadata')
        return {'build': '1.74.0.0.104319', 'read_only': True, 'native_instruction_guards_verified': True,
                'captured_module': module, 'world': objects[0], 'rejected_pointer_candidates': rejected,
                'native_loading_gate_counter': struct.unpack_from('<i', image, 0x3293848)[0],
                'probe_callback_metadata': callbacks[0] if callbacks else None,
                'scope': 'Captured world/owner identity and state only; map/session/controller initialization unverified.'}
    finally: dump.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable'); parser.add_argument('dump')
    args = parser.parse_args()
    print(json.dumps(inspect(args.executable, args.dump), indent=2))
