"""Written bit vectors only; no captures, private identifiers or assets."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from instance_bits import Reader,Writer
from instance_entities import (PlaceableCreate,DefinitionCreate,read_placeable_creates,
                             write_placeable_creates,read_entity_creates,write_entity_creates)


class EntityTests(unittest.TestCase):
    def test_independent_known_bit_vector_and_alignment(self):
        # Explicit LSB field concatenation: count, ID, module chain, create.
        fields=[(1,7),(0,2),(1,1),(0,1),(0x301,16),(1,1),
                (1,1),(0,1),(1,1),(0,2),(1,1),(0,1),(1,1),
                (1,2),(42,14),(1,1),(0x1234,32),(0,1),(0,8),(0,1)]
        raw=position=0
        for value,width in fields:raw|=value<<position;position+=width
        data=raw.to_bytes((position+7)//8,'little')
        self.assertEqual(position,95)
        expected=[PlaceableCreate(0x80000301,0x1234)]
        reader=Reader(data,bit_count=position)
        self.assertEqual(read_placeable_creates(reader),expected)
        self.assertEqual(reader.position,position)
        for prefix in (0,1,7,31):
            writer=Writer();writer.write(0,prefix);write_placeable_creates(writer,expected)
            reader=Reader(writer.finish(),bit_count=writer.bit_count);reader.read(prefix)
            self.assertEqual(read_placeable_creates(reader),expected)
            self.assertEqual(reader.position,prefix+position)
        writer=Writer();write_placeable_creates(writer,expected)
        self.assertEqual(writer.finish(),data)

    def test_index_widths_multiple_and_empty_sections(self):
        for indices in ([],[1,255,256,65535,65536,0x1fffffff]):
            records=[PlaceableCreate(0x80000000|index,i+1) for i,index in enumerate(indices)]
            writer=Writer();write_placeable_creates(writer,records)
            reader=Reader(writer.finish(),bit_count=writer.bit_count)
            self.assertEqual(read_placeable_creates(reader),records)
            self.assertEqual(reader.position,writer.bit_count)
        writer=Writer();write_placeable_creates(writer,[PlaceableCreate(0x80000001,1)]*127)
        self.assertEqual(len(read_placeable_creates(Reader(writer.finish()))),127)

    def test_truncated_and_unsupported_module_payloads(self):
        writer=Writer();write_placeable_creates(writer,[PlaceableCreate(0x80000301,0x1234)])
        for count in range(writer.bit_count):
            with self.assertRaises(ValueError):read_placeable_creates(Reader(writer.finish(),bit_count=count))
        # Corrupt class, module2 optional B, op, length, placeable/extra/components/end.
        for bit in (7,32,37,39,52,85,86,94):
            corrupted=(writer._bits^(1<<bit)).to_bytes(len(writer.finish()),'little')
            with self.assertRaises(ValueError):read_placeable_creates(Reader(corrupted,bit_count=writer.bit_count))

    def test_record_type_class_and_bounds(self):
        valid=PlaceableCreate(0x80000001,1)
        for records in ((valid,),[valid]*128,[None],[PlaceableCreate(True,1)],
                        [PlaceableCreate(0x80000000,1)],[PlaceableCreate(0xc0000001,1)],
                        [PlaceableCreate(-1,1)],[PlaceableCreate(0x180000001,1)],
                        [PlaceableCreate(0x80000001,True)],[PlaceableCreate(0x80000001,0)],
                        [PlaceableCreate(0x80000001,1<<32)]):
            with self.assertRaises(ValueError):write_placeable_creates(Writer(),records)
        with self.assertRaises(ValueError):read_placeable_creates(b'')

    def test_definition_known_vector_and_mixed_sections(self):
        fields=[(1,7),(0,2),(1,1),(0,1),(0x301,16),(1,1),(1,1),(0,1),
                (1,1),(0,2),(1,1),(0,1),(1,1),(1,2),(51,14),(0,1),
                (0,2),(0x1234,32),(0,8),(0,8),(0,1)]
        raw=position=0
        for value,width in fields:raw|=value<<position;position+=width
        data=raw.to_bytes((position+7)//8,'little')
        expected=[DefinitionCreate(0x80000301,0x0400000000001234)]
        self.assertEqual(position,104)
        self.assertEqual(read_entity_creates(Reader(data,bit_count=position)),expected)
        writer=Writer();write_entity_creates(writer,expected)
        self.assertEqual(writer.finish(),data)
        self.assertEqual(writer.bit_count,position)
        with self.assertRaises(ValueError):read_placeable_creates(Reader(data))
        with self.assertRaises(ValueError):write_placeable_creates(Writer(),expected)
        records=[PlaceableCreate(0x80000001,7),*expected,
                 DefinitionCreate(0x80010000,0x04000000ffffffff)]
        for prefix in (0,5,17):
            writer=Writer();writer.write(0,prefix);write_entity_creates(writer,records)
            reader=Reader(writer.finish(),bit_count=writer.bit_count);reader.read(prefix)
            self.assertEqual(read_entity_creates(reader),records)
            self.assertEqual(reader.position,writer.bit_count)

    def test_definition_truncation_optional_forms_and_bounds(self):
        valid=DefinitionCreate(0x80000301,0x0400000000001234)
        writer=Writer();write_entity_creates(writer,[valid])
        for count in range(writer.bit_count):
            with self.assertRaises(ValueError):read_entity_creates(Reader(writer.finish(),bit_count=count))
        for bit in (38,52,53,54,87,95,103):
            corrupted=(writer._bits^(1<<bit)).to_bytes(len(writer.finish()),'little')
            with self.assertRaises(ValueError):read_entity_creates(Reader(corrupted,bit_count=writer.bit_count))
        for guid in (True,0,-1,0x0400000000000000,0x0410000000000001,
                     0x0400000100000001,0x10400000000000001):
            writer=Writer();writer.write(3,2)
            with self.assertRaises(ValueError):write_entity_creates(writer,[DefinitionCreate(0x80000301,guid)])
            self.assertEqual(writer.bit_count,2)
        for records in ((valid,),[valid]*128,[None],[DefinitionCreate(0xc0000001,valid.definition_guid)]):
            with self.assertRaises(ValueError):write_entity_creates(Writer(),records)


if __name__=='__main__':unittest.main()
