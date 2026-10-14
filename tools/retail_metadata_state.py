"""Read-only metadata registration/processing snapshots for build 104319.

Exports counts, booleans and raw markers only. Registration is distinct from
successful processing or an active/ready content context. No identifiers,
digests, keys, native addresses or payloads are exported.
"""
import struct

METADATA_VFT = 0x2611278
OWNER_MASK = 0xf3b530a5300e4c1a
DEFAULT_IDENTIFIER_RVA = 0x321ff30
MAX_ENTRIES = 4096


def metadata_state(dump, limit=8):
    from retail_login_state import inspect, ROOT_RVA, COOKIE_RVA, TABLE_MASK
    if type(limit) is not int or not 1 <= limit <= 8:
        raise ValueError('metadata sample bound')
    inspect(dump)
    image = dump.image_base

    def read(address, size):
        data = dump.read(address, size)
        if len(data) != size:
            raise ValueError('incomplete metadata diagnostic memory')
        return data

    def u(address):
        return struct.unpack('<Q', read(address, 8))[0]

    root = u(image + ROOT_RVA)
    table = ((TABLE_MASK - u(image + COOKIE_RVA)) & ((1 << 64) - 1)) ^ u(root + 0x140)
    if not table or table % 8:
        raise ValueError('metadata context table alignment')
    candidates = []
    for pointer in struct.unpack('<256Q', read(table, 2048)):
        if not pointer or pointer % 8:
            continue
        # Unused table slots and unrelated components need not contain a
        # readable metadata-service layout. Only an exact vtable is a match.
        identity = dump.read(pointer, 16)
        if len(identity) != 16:
            continue
        vft, owner = struct.unpack('<QQ', identity)
        if vft == image + METADATA_VFT:
            if owner ^ OWNER_MASK != root:
                raise ValueError('metadata owner identity differs')
            candidates.append(pointer)
    if len(candidates) != 1:
        raise ValueError('metadata service identity count differs')
    data = read(candidates[0], 0x1a8)
    array, count = struct.unpack_from('<QQ', data, 0x150)
    if count > MAX_ENTRIES or (count and (not array or array % 8)):
        raise ValueError('metadata entry array bound/alignment')
    terminal = data[0x169]
    if terminal not in (0, 1):
        raise ValueError('metadata initialization flag differs')
    default = read(image + DEFAULT_IDENTIFIER_RVA, 32)
    entries, seen = [], set()
    for pointer in struct.unpack('<' + 'Q' * min(count, limit), read(array, min(count, limit) * 8)):
        if not pointer or pointer % 8 or pointer in seen:
            raise ValueError('metadata entry identity/alignment')
        seen.add(pointer)
        entry = read(pointer, 0x90)
        # The consumer at 0x67fd70 increments +0x88 for each completed
        # kind-14 attempt and writes clock+delay at +0x80 when retrying.
        # These are a counter and deadline, not an action state/pointer.
        flags = struct.unpack_from('<I', entry, 0x78)[0]
        entries.append(dict(identifier_is_default=entry[:32] == default,
                            format_field=struct.unpack_from('<I', entry, 0x24)[0],
                            processing_flags=flags,
                            content_present=bool(flags & 1),
                            acquisition_in_flight=bool(flags & 0x40),
                            acquisition_failed=bool(flags & 0x80),
                            retry_deadline_set=bool(struct.unpack_from('<Q', entry, 0x80)[0]),
                            completed_acquisition_attempts=struct.unpack_from('<I', entry, 0x88)[0]))
    return dict(cached_metadata_entries=count, sampled_entries=len(entries),
                entries_truncated=count > limit,
                current_context_present=bool(struct.unpack_from('<Q', data, 0x1a0)[0]),
                pending_initialization_action=bool(struct.unpack_from('<Q', data, 0x118)[0]),
                initialization_terminal_flag=terminal, entries=entries)
