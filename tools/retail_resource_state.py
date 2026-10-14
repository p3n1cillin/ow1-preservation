"""Read-only resource gates for final-client WAITING world requests.

Numeric memory layout observations for build 104319. Reports flags/counts/raw
load states only; no resource GUIDs, pointers, table bytes or payloads escape.
Catalogue presence is distinct from an initiated/completed resource load.
"""
import struct
from collections import Counter

CATALOGUE_ROOT_RVA = 0x321f338
CACHE_BUCKETS_RVA = 0x321f358
CACHE_COUNT_RVA = 0x321f35c
CACHE_TABLE_RVA = 0x321f360
HASH_TABLE_RVA = 0x2788430
MAX_ENTRIES = 1 << 20
MAX_CHAIN = 1024
MAX_REQUEST_RESOURCES = 4096
MAX_CACHE_SNAPSHOT_ENTRIES = 4096
MAP_HEADER_TYPE = 0x0790000000000000


class ResourceReader:
    """Bounded saved-memory reader; caller validates the final-client profile."""
    def __init__(self, dump):
        self.dump = dump
        self.base = dump.image_base
        self.hash_table = struct.unpack('<256Q', self.read(self.base + HASH_TABLE_RVA, 2048))
        # A reflected CRC table is linear over its byte input. Reject an
        # incomplete/different table rather than guessing lookup results.
        if not self.hash_table[128] or any(
            self.hash_table[i] != self.hash_table[i & (i - 1)] ^ self.hash_table[i & -i]
            for i in range(1, 256)
        ) or self.hash_table[0]:
            raise ValueError('resource hash table profile differs')
        self.bound_table(self.uint(self.base + CACHE_BUCKETS_RVA, 4),
                         self.uint(self.base + CACHE_COUNT_RVA, 4))

    def read(self, address, size):
        value = self.dump.read(address, size)
        if len(value) != size:
            raise ValueError('incomplete resource diagnostic memory')
        return value

    def uint(self, address, size=8):
        return int.from_bytes(self.read(address, size), 'little')

    @staticmethod
    def bound_table(buckets, count):
        if buckets > MAX_ENTRIES or count > MAX_ENTRIES or (buckets and buckets & (buckets - 1)):
            raise ValueError('resource table bound/profile differs')

    def hash_guid(self, guid):
        value = 0
        for byte in struct.pack('<Q', guid):
            value = (value >> 8) ^ self.hash_table[(value ^ byte) & 255]
        return value

    def lookup(self, node, key, key_offset):
        seen = set()
        for _ in range(MAX_CHAIN):
            if not node:
                return 0
            if node % 8 or node in seen:
                raise ValueError('resource chain alignment/cycle')
            seen.add(node)
            if self.uint(node + key_offset) == key:
                return self.uint(node + 8)
            node = self.uint(node)
        raise ValueError('resource chain bound')

    def catalogue_present(self, guid):
        catalogue = self.uint(self.base + CATALOGUE_ROOT_RVA)
        if not catalogue or catalogue % 8:
            raise ValueError('resource catalogue identity missing')
        table = catalogue + 0x60
        buckets, count = self.uint(table + 0x10, 4), self.uint(table + 0x14, 4)
        self.bound_table(buckets, count)
        if not count:
            return False
        # Integer key mixing, independently expressed with explicit uint64
        # truncation; the native catalogue compares the full GUID in each node.
        mask = (1 << 64) - 1
        value = ((guid << 21) + (~guid & mask)) & mask
        value ^= value >> 24
        value = value * 0x109 & mask
        value ^= value >> 14
        value = value * 0x15 & mask
        index = ((((value >> 28) ^ value) * 0x80000001) & 0xffffffff) & (buckets - 1) if buckets else 0
        root = self.uint(table + 0x18)
        if not root or root % 8:
            raise ValueError('resource catalogue buckets missing')
        return bool(self.lookup(self.uint(root + index * 8), guid, 0x18))

    def load_state(self, guid):
        buckets = self.uint(self.base + CACHE_BUCKETS_RVA, 4)
        count = self.uint(self.base + CACHE_COUNT_RVA, 4)
        self.bound_table(buckets, count)
        obj = 0
        if count:
            key = self.hash_guid(guid)
            root = self.uint(self.base + CACHE_TABLE_RVA)
            if not root or root % 8:
                raise ValueError('resource cache buckets missing')
            index = key & (buckets - 1) if buckets else 0
            obj = self.lookup(self.uint(root + index * 8), key, 0x10)
        if obj and obj % 8:
            raise ValueError('resource object alignment')
        return dict(cache_entry_present=bool(obj), raw_load_state=self.uint(obj + 0xac, 1) if obj else 0)

    def resource(self, guid):
        return dict(catalogue_present=self.catalogue_present(guid), **self.load_state(guid))

    def cache_summary(self):
        """Aggregate raw states of existing objects; never initiate a load.

        This diagnostic has a smaller traversal budget than single-key lookup.
        A count mismatch (including a changing live table) rejects the snapshot.
        """
        buckets = self.uint(self.base + CACHE_BUCKETS_RVA, 4)
        count = self.uint(self.base + CACHE_COUNT_RVA, 4)
        self.bound_table(buckets, count)
        if max(buckets, count) > MAX_CACHE_SNAPSHOT_ENTRIES:
            raise ValueError('resource cache snapshot bound')
        nodes, objects, states = set(), set(), Counter()
        if count:
            table = self.uint(self.base + CACHE_TABLE_RVA)
            if not table or table % 8:
                raise ValueError('resource cache buckets missing')
            for index in range(max(1, buckets)):
                node = self.uint(table + index * 8)
                chain_count = 0
                while node:
                    if node % 8 or node in nodes or chain_count >= MAX_CHAIN:
                        raise ValueError('resource cache snapshot chain alignment/cycle/bound')
                    if len(nodes) >= count:
                        raise ValueError('resource cache snapshot count differs')
                    nodes.add(node)
                    chain_count += 1
                    obj = self.uint(node + 8)
                    if not obj or obj % 8:
                        raise ValueError('resource cache snapshot object alignment')
                    if obj not in objects:
                        objects.add(obj)
                        states[str(self.uint(obj + 0xac, 1))] += 1
                    node = self.uint(node)
        if len(nodes) != count:
            raise ValueError('resource cache snapshot count differs')
        return dict(entry_count=count, unique_resource_objects=len(objects),
                    raw_load_state_counts=dict(sorted(states.items())))


def resource_cache_state(dump):
    from retail_login_state import inspect
    inspect(dump)
    return ResourceReader(dump).cache_summary()


def world_resource_states(dump, limit=8):
    """Inspect only WAITING requests, without invoking loaders or changing state."""
    from retail_login_state import inspect, WORLD_VFT, WORLD_STATES, IMAGE_SIZE
    if type(limit) is not int or not 1 <= limit <= 8:
        raise ValueError('world resource manager bound')
    inspect(dump)
    reader = ResourceReader(dump)
    result = []
    for address in dump.find_all(struct.pack('<Q', dump.image_base + WORLD_VFT)):
        if address % 8 or dump.image_base <= address < dump.image_base + IMAGE_SIZE:
            continue
        state = reader.uint(address + 0x18, 1)
        if state >= len(WORLD_STATES):
            raise ValueError('unknown world state value')
        request = reader.uint(address + 0x20)
        report = dict(state=WORLD_STATES[state], world_request_pending=bool(request))
        if request and state == 2:
            if request % 8:
                raise ValueError('world request alignment')
            flag = reader.uint(address + 0x41, 1)
            if flag not in (0, 1):
                raise ValueError('world request submission flag')
            header = MAP_HEADER_TYPE | (reader.uint(request) & 0xffffffff)
            optional = reader.uint(request + 8)
            # Native request copy (0x590d50) retains the 20300 +0x520 array
            # here. This is distinct from the settings array at +0x68.
            resources = reader.uint(request + 0xf8)
            resource_count = struct.unpack('<i', reader.read(request + 0x100, 4))[0]
            if not 0 <= resource_count <= MAX_REQUEST_RESOURCES:
                raise ValueError('world request resource count bound')
            if resource_count:
                if not resources or resources % 8:
                    raise ValueError('world request resource array alignment')
                reader.read(resources, resource_count * 8)
            report.update(request_submit_flag=bool(flag), map_header=reader.resource(header),
                          extra_resource_count=resource_count,
                          optional_resource_present=bool(optional),
                          optional_resource=reader.resource(optional | 0x10000000000) if optional else None)
        result.append(report)
        if len(result) >= limit:
            break
    return dict(resource_cache_count=reader.uint(reader.base + CACHE_COUNT_RVA, 4), managers=result)
