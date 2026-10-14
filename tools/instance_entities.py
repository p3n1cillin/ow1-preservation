"""Bounded 104319 server entity section for minimal entity creates.

Call after the server module prefixes, at the seven-bit entity count. The
observed non-hot-reload profile has empty modules 0..3, module-4 create data,
and an entity-chain terminator. Definition creates use the neutral 32-bit type-3
resource form, zero transform flags and no network component state. Creating an
entity does not establish a playable hero. The placeable-only wrappers remain
strict. This is not a session encoder.
Authenticate incoming datagrams before decoding. No client assets included.
"""
from dataclasses import dataclass
from instance_bits import Reader, Writer


@dataclass(frozen=True)
class PlaceableCreate:
    entity_id: int
    placeable_id: int


@dataclass(frozen=True)
class DefinitionCreate:
    entity_id: int
    definition_guid: int


def _index(entity_id):
    if type(entity_id) is not int or entity_id >> 29 != 4:
        raise ValueError('entity create class')
    index = entity_id & 0x1fffffff
    if not index:raise ValueError('invalid zero entity index')
    return index


def write_entity_creates(bits, records):
    if type(bits) is not Writer or type(records) is not list or len(records)>127:
        raise ValueError('entity section type/count')
    # Validate records before modifying the caller's stream.
    for record in records:
        if type(record) not in (PlaceableCreate,DefinitionCreate):raise ValueError('entity record type')
        _index(record.entity_id)
        if type(record) is PlaceableCreate:
            if type(record.placeable_id) is not int or not 0<record.placeable_id<1<<32:
                raise ValueError('placeable identifier bound')
        elif (type(record.definition_guid) is not int or record.definition_guid>>32!=0x04000000
              or not record.definition_guid&0xffffffff):
            raise ValueError('definition resource type/bound')
    bits.write(len(records),7)
    for record in records:
        index = _index(record.entity_id)
        bits.write(0,2) # Native ID class selector: top bits 1gg, here 100.
        if index<256:bits.write(0,1);bits.write(index,8)
        elif index<65536:bits.write(1,1);bits.write(0,1);bits.write(index,16)
        else:bits.write(1,1);bits.write(1,1);bits.write(index,32)
        bits.write(1,1) # Module 0 has no per-entity data.
        bits.write(1,1);bits.write(0,1) # Module 1 empty.
        bits.write(1,1);bits.write(0,2) # Module 2 has TWO optional sections.
        bits.write(1,1);bits.write(0,1) # Module 3 empty.
        placeable=type(record) is PlaceableCreate
        bits.write(1,1);bits.write(1,2);bits.write(42 if placeable else 51,14)
        bits.write(int(placeable),1)
        if placeable:
            bits.write(record.placeable_id,32);bits.write(0,1)
        else:
            bits.write(0,2);bits.write(record.definition_guid&0xffffffff,32)
            bits.write(0,8) # Neutral transform flags, no optional fields.
        bits.write(0,8) # No network component data.
        bits.write(0,1) # End this entity's module chain.


def read_entity_creates(bits):
    if type(bits) is not Reader:raise ValueError('entity reader type')
    records=[]
    def expect(value,width):
        if bits.read(width)!=value:raise ValueError('unsupported entity module profile')
    for _ in range(bits.read(7)):
        expect(0,2)
        if not bits.read(1):index=bits.read(8)
        elif not bits.read(1):index=bits.read(16)
        else:index=bits.read(32)
        if not 0<index<1<<29:raise ValueError('placeable entity index bound')
        expect(1,1)
        expect(1,1);expect(0,1)
        expect(1,1);expect(0,2)
        expect(1,1);expect(0,1)
        expect(1,1);expect(1,2)
        length=bits.read(14)
        if bits.read(1):
            if length!=42:raise ValueError('unsupported placeable payload length')
            placeable=bits.read(32)
            if not placeable:raise ValueError('placeable identifier bound')
            expect(0,1)
            record=PlaceableCreate(0x80000000|index,placeable)
        else:
            if length!=51:raise ValueError('unsupported definition payload length')
            expect(0,2) # Strict neutral type-3 resource index form.
            resource=bits.read(32)
            if not resource:raise ValueError('definition resource index bound')
            expect(0,8) # Transform flags.
            record=DefinitionCreate(0x80000000|index,0x0400000000000000|resource)
        expect(0,8);expect(0,1)
        records.append(record)
    return records


def write_placeable_creates(bits, records):
    if type(records) is not list or any(type(record) is not PlaceableCreate for record in records):
        raise ValueError('placeable record type')
    write_entity_creates(bits,records)


def read_placeable_creates(bits):
    records=read_entity_creates(bits)
    if any(type(record) is not PlaceableCreate for record in records):
        raise ValueError('unsupported definition in placeable section')
    return records
