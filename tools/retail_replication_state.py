"""Read-only selected-entity gates for the original 104319 world update.

Reports booleans and bounded counts only, never entity IDs or pointers.
Resolving an entity is one prerequisite, not proof of completed replication.
Component 44 is required by the traced first-person owner lookup; its presence
alone does not establish a controlled actor, hero initialization or gameplay.
"""
import struct
from retail_login_state import inspect, WORLD_VFT, WORLD_STATES, IMAGE_SIZE, TABLE_MASK, COOKIE_RVA

MASK = (1 << 64) - 1
OWNER_VFT = 0x260be40
SECONDARY_VFT = 0x2618220
REPLICATION_SLOT_VFT = 0x2610cf0
PROFILES = ((0x5881c4, bytes.fromhex('8b02898198020000')),
            (0x78935a, bytes.fromhex('8b18895c2468')),
            (0x78ac02, bytes.fromhex('488b5718')),
            (0x78ac12, bytes.fromhex('8b420885c0')),
            (0x5fd5a0, bytes.fromhex('c6014f488bc1c3')),
            (0x78ce75, bytes.fromhex('8b80b0000000')),
            (0xbd59a0, bytes.fromhex('48b80000000000100000')))


def replication_gates(dump, limit=8):
    if type(limit) is not int or not 1 <= limit <= 8:
        raise ValueError('world manager limit')
    inspect(dump)
    image = dump.image_base

    def read(address, size):
        data = dump.read(address, size)
        if len(data) != size:raise ValueError('incomplete replication diagnostic memory')
        return data

    def u(address, size=8):return int.from_bytes(read(address, size), 'little')

    def pointer(value):
        if not value or value % 8 or value >= 0x800000000000:
            raise ValueError('replication pointer bound/alignment')
        return value

    for rva, expected in PROFILES:
        if read(image+rva, len(expected)) != expected:
            raise ValueError('replication getter profile differs')
    if u(image+0x7d2244+2*4, 4) != 0x7d2079:
        raise ValueError('selected-entity dispatch profile differs')
    invalid = u(image+0x3241288, 4)
    context_cookie = u(image+COOKIE_RVA)
    owner_key = u(image+0x2ee48a1) ^ 0x4dfd564467c27b96
    cookie = u(image+0x2ee53a8)
    rotated = ((cookie >> 4) | (cookie << 60)) & MASK
    table_key = (0x042b51ef9b84a901 + 2*rotated) & MASK
    rows = []
    for world in dump.find_all(struct.pack('<Q', image+WORLD_VFT)):
        if world % 8 or image <= world < image+IMAGE_SIZE:continue
        if u(world+0x10) != image+SECONDARY_VFT:continue
        state = u(world+0x18, 1)
        if state >= len(WORLD_STATES):raise ValueError('unknown world state')
        owner_encoded = u(world+8)
        owner = pointer(owner_encoded ^ owner_key)
        if u(owner) != image+OWNER_VFT:raise ValueError('world owner identity')
        selected = u(owner+0x298, 4)
        valid = selected != invalid and selected & 0x1fffffff != 0x1fffffff
        row = dict(state=WORLD_STATES[state], selected_entity_valid=valid)
        # Original 0x641250 context getter selects slot 79 via 0x5fd5a0.
        contexts_encoded = u(owner+0x140)
        contexts = pointer(contexts_encoded ^ ((TABLE_MASK-context_cookie) & MASK))
        slot = pointer(u(contexts+79*8))
        if u(slot) != image+REPLICATION_SLOT_VFT:raise ValueError('replication slot identity')
        job = u(slot+0x18)
        row['replication_context_present'] = bool(job)
        if job:
            pointer(job)
            # This job is a plain structure, not an object with a vtable.
            queued, pending = u(job+0x18,4), u(job+0x128,4)
            marker = u(job+0x148,1)
            if queued > 4096 or pending > 4096:raise ValueError('replication queue count bound')
            if marker not in (0,1):raise ValueError('replication completion marker bound')
            row.update(queued_record_count=queued, pending_count=pending,
                       completion_marker=bool(marker))
            if (u(job+0x18,4) != queued or u(job+0x128,4) != pending
                    or u(job+0x148,1) != marker):
                raise ValueError('replication queue changed')
        if valid:
            encoded = u(owner+0x18)
            table = pointer(encoded ^ table_key)
            bucket = table+(selected & 0xfff)*16
            array, count = u(bucket), u(bucket+8, 4)
            if count > 4096:raise ValueError('selected entity bucket count bound')
            if count:pointer(array)
            entries = read(array, count*16) if count else b''
            matches, same_index, obj = 0, 0, 0
            for offset in range(0, len(entries), 16):
                entity = struct.unpack_from('<I', entries, offset)[0]
                if entity & 0x1fffffff == selected & 0x1fffffff:same_index += 1
                if entity == selected:
                    matches += 1
                    obj = struct.unpack_from('<Q', entries, offset+8)[0]
                    if obj:pointer(obj)
            if matches > 1:raise ValueError('duplicate selected entity record')
            if obj:
                # Native entity structures store ID at +b0 and mask word 0 at +88.
                # The guarded component getter tests word 0, bit 44.
                native_id = u(obj+0xb0, 4)
                component_mask = u(obj+0x88)
                if native_id != selected:raise ValueError('selected entity object identity differs')
                row.update(selected_entity_native_id_matches=True,
                           first_person_owner_component_present=bool(component_mask & (1 << 44)))
                if u(obj+0xb0,4) != native_id or u(obj+0x88) != component_mask:
                    raise ValueError('selected entity object changed')
            row.update(selected_bucket_count=count, selected_entity_record_present=bool(matches),
                       selected_entity_object_present=bool(obj),
                       same_index_record_present=bool(same_index),
                       generation_mismatch=bool(same_index and not matches))
            if u(owner+0x18) != encoded or u(bucket) != array or u(bucket+8,4) != count:
                raise ValueError('selected entity table changed')
        if (u(world+0x18,1) != state or u(world+8) != owner_encoded
                or u(owner+0x298,4) != selected or u(owner+0x140) != contexts_encoded
                or u(slot+0x18) != job):
            raise ValueError('replication state changed')
        rows.append(row)
        if len(rows) > limit:raise ValueError('world manager count bound')
    if (u(image+0x2ee53a8) != cookie or u(image+0x2ee48a1)^0x4dfd564467c27b96 != owner_key
            or u(image+0x3241288,4) != invalid or u(image+COOKIE_RVA) != context_cookie):
        raise ValueError('replication decoding inputs changed')
    return dict(managers=rows)
