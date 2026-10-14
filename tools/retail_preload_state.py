"""Read-only engine preloader snapshots for final client build 104319.

Reports bounded counts and submission flags, never resource identifiers or
native pointers. Empty queues describe the saved instant, not earlier activity
or the cause of a stalled world. The engine preloader is separate from the
world-state manager and resource load cache.
"""
import struct

PRELOADER_SLOT = 39
PRELOADER_VFT = 0x2610910
OWNER_MASK = 0xf3b530a5300e4c1a
MAX_REQUESTS = 4096
MAP_HEADER_TYPE = 0x0790000000000000
RESOURCE_TYPE_MASK = 0x0fff000000000000


def preload_state(dump):
    from retail_login_state import inspect, ROOT_RVA, COOKIE_RVA, TABLE_MASK
    inspect(dump)
    image = dump.image_base

    def read(address, size):
        data = dump.read(address, size)
        if len(data) != size:
            raise ValueError('incomplete preloader diagnostic memory')
        return data

    def u(address):
        return struct.unpack('<Q', read(address, 8))[0]

    root = u(image + ROOT_RVA)
    table = ((TABLE_MASK - u(image + COOKIE_RVA)) & ((1 << 64) - 1)) ^ u(root + 0x140)
    if not table or table % 8:
        raise ValueError('preloader context table alignment')
    service = u(table + PRELOADER_SLOT * 8)
    if not service or service % 8:
        raise ValueError('preloader service alignment')
    vft, owner = struct.unpack('<QQ', read(service, 16))
    if vft != image + PRELOADER_VFT or owner ^ OWNER_MASK != root:
        raise ValueError('preloader service identity differs')

    def requests(pointer_offset, count_offset, stride, retained):
        array = u(service + pointer_offset)
        count = struct.unpack('<i', read(service + count_offset, 4))[0]
        if not 0 <= count <= MAX_REQUESTS:
            raise ValueError('preloader request count bound')
        if count and (not array or array % 8):
            raise ValueError('preloader request array alignment')
        headers = submitted = submitted_headers = conditional = 0
        for index in range(count):
            row = read(array + index * stride, stride)
            # The native descriptor builder copies the resource at +8, its
            # conditional key at +0, and priority at +0x20 into request options.
            guid = struct.unpack_from('<Q', row, 8)[0]
            header = (guid & RESOURCE_TYPE_MASK) == MAP_HEADER_TYPE
            headers += header
            conditional += bool(struct.unpack_from('<Q', row)[0])
            if retained:
                # Native submission sets +0x44 after calling the loader;
                # withdrawal clears it. This is not a completion flag.
                flag = row[0x44]
                if flag not in (0, 1):
                    raise ValueError('preloader submission flag differs')
                submitted += flag
                submitted_headers += flag if header else 0
        result = dict(request_count=count, map_header_request_count=headers,
                      conditional_request_count=conditional)
        if retained:
            result.update(submitted_request_count=submitted,
                          submitted_map_header_request_count=submitted_headers)
        return result

    return dict(configured=requests(0x2678, 0x2680, 64, False),
                retained=requests(0x58, 0x60, 72, True))
