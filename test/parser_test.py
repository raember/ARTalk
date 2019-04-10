import unittest
from artalk.parser import Parser, Code, BlockFactory


class ParserTest(unittest.TestCase):
    def test_parse(self):
        document = """
[Constant RAM Writes]
01234567 89ABCDEF
11234567 000089AB
21234567 00000089

[Conditional 32-Bit Code Types]
31234567 89ABCDEF
41234567 89ABCDEF
51234567 89ABCDEF
61234567 89ABCDEF

[Conditional 16-Bit + Masking RAM Writes]
71234567 89ABCDEF
81234567 89ABCDEF
91234567 89ABCDEF
A1234567 89ABCDEF
"""
        parser = Parser()
        codes = parser.parse(document)
        self.assertEqual(3, len(codes))
        code0 = codes[0]
        code1 = codes[1]
        code2 = codes[2]
        self.assertEqual("Constant RAM Writes", code0.title)
        self.assertEqual(3, len(code0.blocks))
        block0 = code0.blocks[0]
        block1 = code0.blocks[1]
        block2 = code0.blocks[2]
        from artalk.parser import WWrite, SWrite, BWrite
        self.assertEqual(WWrite, type(block0))
        self.assertEqual("0x89ABCDEF", block0.hex_value())
        self.assertEqual(SWrite, type(block1))
        self.assertEqual("0x89AB", block1.hex_value())
        self.assertEqual(BWrite, type(block2))
        self.assertEqual("0x89", block2.hex_value())

        self.assertEqual("Conditional 32-Bit Code Types", code1.title)
        self.assertEqual(4, len(code1.blocks))
        block0 = code1.blocks[0]
        block1 = code1.blocks[1]
        block2 = code1.blocks[2]
        block3 = code1.blocks[3]
        from artalk.parser import WGreaterThan, WLessThan, WEqualTo, WNotEqualTo
        self.assertEqual(WGreaterThan, type(block0))
        self.assertEqual("0x89ABCDEF", block0.hex_value())
        self.assertEqual(WLessThan, type(block1))
        self.assertEqual("0x89ABCDEF", block1.hex_value())
        self.assertEqual(WEqualTo, type(block2))
        self.assertEqual("0x89ABCDEF", block2.hex_value())
        self.assertEqual(WNotEqualTo, type(block3))
        self.assertEqual("0x89ABCDEF", block2.hex_value())

        self.assertEqual("Conditional 16-Bit + Masking RAM Writes", code2.title)
        self.assertEqual(4, len(code2.blocks))
        block0 = code2.blocks[0]
        block1 = code2.blocks[1]
        block2 = code2.blocks[2]
        block3 = code2.blocks[3]
        from artalk.parser import WGreaterThan, WLessThan, WEqualTo, WNotEqualTo
        self.assertEqual(WGreaterThan, type(block0))
        self.assertEqual("0x89ABCDEF", block0.hex_value())
        self.assertEqual(WLessThan, type(block1))
        self.assertEqual("0x89ABCDEF", block1.hex_value())
        self.assertEqual(WEqualTo, type(block2))
        self.assertEqual("0x89ABCDEF", block2.hex_value())
        self.assertEqual(WNotEqualTo, type(block3))
        self.assertEqual("0x89ABCDEF", block2.hex_value())


class CodeTest(unittest.TestCase):
    def test_isTitle(self):
        self.assertTrue(Code.is_title("[Pokémon Generator]"))
        self.assertTrue(Code.is_title("[ *  Pokémon Generator    ]"))
        self.assertFalse(Code.is_title("[]"))
        self.assertFalse(Code.is_title(""))
        self.assertFalse(Code.is_title("Pokémon Generator"))
        self.assertFalse(Code.is_title("{Pokémon Generator}"))
        self.assertFalse(Code.is_title("(Pokémon Generator)"))

    def test_init(self):
        code = Code("[Pokémon Generator]")
        self.assertIsNotNone(code)
        self.assertEqual("Pokémon Generator", code.title)

    def test_parseBlock(self):
        code = Code("[Pokémon Generator]")
        self.assertEqual(0, len(code.blocks))
        code.parse_block("  D3000000   00000000  ")
        self.assertEqual(1, len(code.blocks))
        self.assertRaises(Exception, code.parse_block, "ff0f0f0f00f0")


class BlockFactoryTest(unittest.TestCase):
    def setUp(self):
        self.factory = BlockFactory()

    def test_canCreateBlockFrom(self):
        self.assertTrue(self.factory.can_create_block_from("D3000000 00000000"))
        self.assertTrue(self.factory.can_create_block_from("d3000000 00000000"))
        self.assertTrue(self.factory.can_create_block_from("08C71DB0 0098967F"))
        self.assertTrue(self.factory.can_create_block_from("  D3000000  00000000  "))
        self.assertTrue(self.factory.can_create_block_from("D300000000000000"))
        self.assertFalse(self.factory.can_create_block_from("G3000000 00000000"))

    def test_WordWriter(self):
        block = self.factory.create_block("01234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import WWrite
        self.assertEqual(WWrite, type(block))
        self.assertEqual("01234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("01234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(2299182302, block.value)
        print(block.hex_address())
        print(block.hex_address(True))
        print(block.hex_value())
        print(block.hex_value(True))
        print(block.hex_value(True, True))
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0x890ABCDE", block.hex_value())

    def test_ShortWriter(self):
        block = self.factory.create_block("11234567 0000BCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SWrite
        self.assertEqual(SWrite, type(block))
        self.assertEqual("11234567", block.first)
        self.assertEqual("0000BCDE", block.second)
        self.assertEqual("11234567 0000BCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(48350, block.value)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0xBCDE", block.hex_value())
        self.assertRaises(Exception, self.factory.create_block, "11234567 890ABCDE")

    def test_ByteWriter(self):
        block = self.factory.create_block("21234567 000000DE")
        self.assertIsNotNone(block)
        from artalk.parser import BWrite
        self.assertEqual(BWrite, type(block))
        self.assertEqual("21234567", block.first)
        self.assertEqual("000000DE", block.second)
        self.assertEqual("21234567 000000DE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(222, block.value)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0xDE", block.hex_value())
        self.assertRaises(Exception, self.factory.create_block, "21234567 890ABCDE")

    def test_WordLessThan(self):
        block = self.factory.create_block("31234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import WGreaterThan
        self.assertEqual(WGreaterThan, type(block))
        self.assertEqual("31234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("31234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(2299182302, block.value)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0x890ABCDE", block.hex_value())

    def test_WordMoreThan(self):
        block = self.factory.create_block("41234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import WLessThan
        self.assertEqual(WLessThan, type(block))
        self.assertEqual("41234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("41234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(2299182302, block.value)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0x890ABCDE", block.hex_value())

    def test_WordEqualTo(self):
        block = self.factory.create_block("51234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import WEqualTo
        self.assertEqual(WEqualTo, type(block))
        self.assertEqual("51234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("51234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(2299182302, block.value)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0x890ABCDE", block.hex_value())

    def test_WordNotEqualTo(self):
        block = self.factory.create_block("61234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import WNotEqualTo
        self.assertEqual(WNotEqualTo, type(block))
        self.assertEqual("61234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("61234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(2299182302, block.value)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0x890ABCDE", block.hex_value())

    def test_ShortLessThan(self):
        block = self.factory.create_block("71234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SGreaterThan
        self.assertEqual(SGreaterThan, type(block))
        self.assertEqual("71234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("71234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(48350, block.value)
        self.assertEqual(35082, block.mask)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0xBCDE", block.hex_value())
        self.assertEqual("0x890A", block.hex_mask())

    def test_ShortMoreThan(self):
        block = self.factory.create_block("81234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SLessThan
        self.assertEqual(SLessThan, type(block))
        self.assertEqual("81234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("81234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(48350, block.value)
        self.assertEqual(35082, block.mask)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0xBCDE", block.hex_value())
        self.assertEqual("0x890A", block.hex_mask())

    def test_ShortEqualTo(self):
        block = self.factory.create_block("91234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SEqualTo
        self.assertEqual(SEqualTo, type(block))
        self.assertEqual("91234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("91234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(48350, block.value)
        self.assertEqual(35082, block.mask)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0xBCDE", block.hex_value())
        self.assertEqual("0x890A", block.hex_mask())

    def test_ShortNotEqualTo(self):
        block = self.factory.create_block("A1234567 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SNotEqualTo
        self.assertEqual(SNotEqualTo, type(block))
        self.assertEqual("A1234567", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual("A1234567 890ABCDE", str(block))
        self.assertEqual(19088743, block.address)
        self.assertEqual(48350, block.value)
        self.assertEqual(35082, block.mask)
        self.assertEqual("0x01234567", block.hex_address())
        self.assertEqual("0xBCDE", block.hex_value())
        self.assertEqual("0x890A", block.hex_mask())

    def test_LoadOffset(self):
        block = self.factory.create_block("B1234567 00000000")
        self.assertIsNotNone(block)
        from artalk.parser import LoadOffset
        self.assertEqual(LoadOffset, type(block))
        self.assertEqual("B1234567", block.first)
        self.assertEqual("00000000", block.second)
        self.assertRaises(Exception, self.factory.create_block, "B1234567 890ABCDE")

    def test_Repeat(self):
        block = self.factory.create_block("C0000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import Repeat
        self.assertEqual(Repeat, type(block))
        self.assertEqual("C0000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.value)
        self.assertRaises(Exception, self.factory.create_block, "C0000001 890ABCDE")

    def test_ConditionEnd(self):
        block = self.factory.create_block("D0000000 00000000")
        self.assertIsNotNone(block)
        from artalk.parser import ConditionEnd
        self.assertEqual(ConditionEnd, type(block))
        self.assertEqual("D0000000", block.first)
        self.assertEqual("00000000", block.second)
        self.assertRaises(Exception, self.factory.create_block, "D0000000 00000001")
        self.assertRaises(Exception, self.factory.create_block, "D0000001 00000000")

    def test_RepetitionEnd(self):
        block = self.factory.create_block("D1000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import RepetitionEnd
        self.assertEqual(RepetitionEnd, type(block))
        self.assertEqual("D1000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.value)
        self.assertRaises(Exception, self.factory.create_block, "D1000001 00000000")

    def test_Reset(self):
        block = self.factory.create_block("D2000000 00000000")
        self.assertIsNotNone(block)
        from artalk.parser import Reset
        self.assertEqual(Reset, type(block))
        self.assertEqual("D2000000", block.first)
        self.assertEqual("00000000", block.second)
        self.assertRaises(Exception, self.factory.create_block, "D2000000 00000001")
        self.assertRaises(Exception, self.factory.create_block, "D2000001 00000000")

    def test_SetOffset(self):
        block = self.factory.create_block("D3000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SetOffset
        self.assertEqual(SetOffset, type(block))
        self.assertEqual("D3000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.value)
        self.assertRaises(Exception, self.factory.create_block, "D3000001 00000000")

    def test_AddToDxData(self):
        block = self.factory.create_block("D4000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import AddToDxData
        self.assertEqual(AddToDxData, type(block))
        self.assertEqual(2299182302, block.value)
        self.assertEqual("D4000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertRaises(Exception, self.factory.create_block, "D4000001 00000000")

    def test_SetDxData(self):
        block = self.factory.create_block("D5000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import SetDxData
        self.assertEqual(SetDxData, type(block))
        self.assertEqual("D5000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.value)
        self.assertRaises(Exception, self.factory.create_block, "D5000001 00000000")

    def test_DxDataWordWrite(self):
        block = self.factory.create_block("D6000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import DxDataWordWrite
        self.assertEqual(DxDataWordWrite, type(block))
        self.assertEqual("D6000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.address)
        self.assertRaises(Exception, self.factory.create_block, "D6000001 00000000")

    def test_DxDataShortWrite(self):
        block = self.factory.create_block("D7000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import DxDataShortWrite
        self.assertEqual(DxDataShortWrite, type(block))
        self.assertEqual("D7000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.address)
        self.assertRaises(Exception, self.factory.create_block, "D7000001 00000000")

    def test_DxDataByteWrite(self):
        block = self.factory.create_block("D8000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import DxDataByteWrite
        self.assertEqual(DxDataByteWrite, type(block))
        self.assertEqual("D8000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.address)
        self.assertRaises(Exception, self.factory.create_block, "D8000001 00000000")

    def test_DxDataWordRead(self):
        block = self.factory.create_block("D9000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import DxDataWordRead
        self.assertEqual(DxDataWordRead, type(block))
        self.assertEqual("D9000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.address)
        self.assertRaises(Exception, self.factory.create_block, "D9000001 00000000")

    def test_DxDataShortRead(self):
        block = self.factory.create_block("DA000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import DxDataShortRead
        self.assertEqual(DxDataShortRead, type(block))
        self.assertEqual("DA000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.address)
        self.assertRaises(Exception, self.factory.create_block, "DA000001 00000000")

    def test_DxDataByteRead(self):
        block = self.factory.create_block("DB000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import DxDataByteRead
        self.assertEqual(DxDataByteRead, type(block))
        self.assertEqual("DB000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.address)
        self.assertRaises(Exception, self.factory.create_block, "DB000001 00000000")

    def test_AddToOffset(self):
        block = self.factory.create_block("DC000000 890ABCDE")
        self.assertIsNotNone(block)
        from artalk.parser import AddToOffset
        self.assertEqual(AddToOffset, type(block))
        self.assertEqual("DC000000", block.first)
        self.assertEqual("890ABCDE", block.second)
        self.assertEqual(2299182302, block.value)
        self.assertRaises(Exception, self.factory.create_block, "DC000001 00000000")

    def test_WaitForButton(self):
        block = self.factory.create_block("DD000000 00000001")
        self.assertIsNotNone(block)
        from artalk.parser import WaitForButton
        self.assertEqual(WaitForButton, type(block))
        self.assertEqual("DD000000", block.first)
        self.assertEqual("00000001", block.second)
        self.assertListEqual(["A"], block.buttons)
        block = self.factory.create_block("DD000000 00000002")
        self.assertIsNotNone(block)
        self.assertListEqual(["B"], block.buttons)
        block = self.factory.create_block("DD000000 00000004")
        self.assertIsNotNone(block)
        self.assertListEqual(["SELECT"], block.buttons)
        block = self.factory.create_block("DD000000 00000008")
        self.assertIsNotNone(block)
        self.assertListEqual(["START"], block.buttons)
        block = self.factory.create_block("DD000000 00000010")
        self.assertIsNotNone(block)
        self.assertListEqual(["RIGHT"], block.buttons)
        block = self.factory.create_block("DD000000 00000020")
        self.assertIsNotNone(block)
        self.assertListEqual(["LEFT"], block.buttons)
        block = self.factory.create_block("DD000000 00000040")
        self.assertIsNotNone(block)
        self.assertListEqual(["UP"], block.buttons)
        block = self.factory.create_block("DD000000 00000080")
        self.assertIsNotNone(block)
        self.assertListEqual(["DOWN"], block.buttons)
        block = self.factory.create_block("DD000000 00000100")
        self.assertIsNotNone(block)
        self.assertListEqual(["R"], block.buttons)
        block = self.factory.create_block("DD000000 00000200")
        self.assertIsNotNone(block)
        self.assertListEqual(["L"], block.buttons)
        block = self.factory.create_block("DD000000 00000400")
        self.assertIsNotNone(block)
        self.assertListEqual(["X"], block.buttons)
        block = self.factory.create_block("DD000000 00000800")
        self.assertIsNotNone(block)
        self.assertListEqual(["Y"], block.buttons)
        block = self.factory.create_block("DD000000 00002000")
        self.assertIsNotNone(block)
        self.assertListEqual(["DEBUG"], block.buttons)
        block = self.factory.create_block("DD000000 00008000")
        self.assertIsNotNone(block)
        self.assertListEqual(["NOT-FOLDED"], block.buttons)
        self.assertRaises(Exception, self.factory.create_block, "DD000001 00000000")
        self.assertRaises(Exception, self.factory.create_block, "DD000000 00000000")
        block = self.factory.create_block("DD000000 00000044")
        self.assertIsNotNone(block)
        self.assertListEqual(["SELECT", "UP"], block.buttons)

    def test_Patch(self):
        block = self.factory.create_block("E0000000 00000008")
        self.assertIsNotNone(block)
        from artalk.parser import Patch
        self.assertEqual(Patch, type(block))
        self.assertEqual("E0000000", block.first)
        self.assertEqual("00000008", block.second)
        self.assertEqual(0, block.address)
        self.assertEqual(8, block.value)
        self.assertEqual(0, len(block.bytes))
        tempBlock = self.factory.create_block("FFFFFFFF 00000000", block)
        self.assertIsNone(tempBlock)
        self.assertEqual(8, len(block.bytes))

    def test_Memory(self):
        block = self.factory.create_block("F7000000 0003FFC0")
        self.assertIsNotNone(block)
        self.assertEqual("F7000000", block.first)
        self.assertEqual("0003FFC0", block.second)
        self.assertEqual(117440512, block.address)
        self.assertEqual(262080, block.value)


if __name__ == '__main__':
    unittest.main()
