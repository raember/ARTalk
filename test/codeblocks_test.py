import unittest
from artalk.codeblocks import MemoryWrite, Conditional32bitCodes, Conditions, Conditional16bitCodes
from artalk.codeblocks import OutOfRangeError
from artalk.codeblocks import WWrite, SWrite, BWrite, WGreaterThan, WLessThan, WEqualTo, WNotEqualTo, \
    SGreaterThan, SLessThan, SEqualTo, SNotEqualTo, LoadOffset, Repeat, ConditionEnd, RepetitionEnd, Reset, SetOffset, \
    AddToDxData, SetDxData, DxDataWordWrite, DxDataShortWrite, DxDataByteWrite, DxDataWordRead, DxDataShortRead, \
    DxDataByteRead, AddToOffset, WaitForButton, Memory


class TestMemoryWrite(unittest.TestCase):
    def test_create_wwrite(self):
        block = MemoryWrite.create(0x12345678, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(WWrite, type(block))
        self.assertEqual("09ABCDEF 12345678", str(block))

    def test_create_swrite(self):
        block = MemoryWrite.create(0x5678, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(SWrite, type(block))
        self.assertEqual("19ABCDEF 00005678", str(block))

    def test_create_bwrite(self):
        block = MemoryWrite.create(0x78, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(BWrite, type(block))
        self.assertEqual("29ABCDEF 00000078", str(block))


class TestWWrite(unittest.TestCase):
    FIRST = 0x00020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = WWrite(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x0000000F", block.hex_value())

    def test_constructor_neg(self):
        WWrite(0xFFFFFFFF, 0xFFFFFFF)
        WWrite(0, 0)
        self.assertRaises(OutOfRangeError, WWrite, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WWrite, 0xFFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, WWrite, 0x100000000, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WWrite, 0xFFFFFFFF, 0x10000000)

    def test_parse(self):
        block = WWrite.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(WWrite, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(15, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x0000000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = WWrite(15, 0x20200)
        self.assertEqual("*((int*)0x00020200 + offset) = 0x0000000F;", block.to_c())
        self.assertEqual("*((int*)0x00020200 + offset) = 0x0000000F /* 15 */;", block.to_c(True))

    def test_to_human_readable(self):
        block = WWrite(15, 0x20200)
        self.assertEqual("Write word 0x0000000F to [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Write word 0x0000000F(15) to [0x00020200 + offset]", block.to_human_readable(True))


class TestSWrite(unittest.TestCase):
    FIRST = 0x10020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = SWrite(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x000F", block.hex_value())

    def test_constructor_neg(self):
        SWrite(0xFFFF, 0xFFFFFFF)
        SWrite(0, 0)
        self.assertRaises(OutOfRangeError, SWrite, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, SWrite, 0xFFFF, -1)
        self.assertRaises(OutOfRangeError, SWrite, 0x10000, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, SWrite, 0xFFFF, 0x10000000)

    def test_parse(self):
        block = SWrite.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(SWrite, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(15, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = SWrite(15, 0x20200)
        self.assertEqual("*((int*)0x00020200 + offset) = 0x000F;", block.to_c())
        self.assertEqual("*((int*)0x00020200 + offset) = 0x000F /* 15 */;", block.to_c(True))

    def test_to_human_readable(self):
        block = SWrite(15, 0x20200)
        self.assertEqual("Write short 0x000F to [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Write short 0x000F(15) to [0x00020200 + offset]", block.to_human_readable(True))


class TestBWrite(unittest.TestCase):
    FIRST = 0x20020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = BWrite(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x0F", block.hex_value())

    def test_constructor_neg(self):
        BWrite(0xFF, 0xFFFFFFF)
        BWrite(0, 0)
        self.assertRaises(OutOfRangeError, BWrite, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, BWrite, 0xFF, -1)
        self.assertRaises(OutOfRangeError, BWrite, 0x100, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, BWrite, 0xFF, 0x10000000)

    def test_parse(self):
        block = BWrite.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(BWrite, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(15, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x0F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = BWrite(15, 0x20200)
        self.assertEqual("*((int*)0x00020200 + offset) = 0x0F;", block.to_c())
        self.assertEqual("*((int*)0x00020200 + offset) = 0x0F /* 15 */;", block.to_c(True))

    def test_to_human_readable(self):
        block = BWrite(15, 0x20200)
        self.assertEqual("Write byte 0x0F to [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Write byte 0x0F(15) to [0x00020200 + offset]", block.to_human_readable(True))


class TestConditional32bitCodes(unittest.TestCase):

    def test_create_wgreaterthan(self):
        block = Conditional32bitCodes.create(0x12345678, Conditions.GREATERTHAN, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(WGreaterThan, type(block))
        self.assertEqual("39ABCDEF 12345678", str(block))

    def test_create_wlessthan(self):
        block = Conditional32bitCodes.create(0x12345678, Conditions.LESSTHAN, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(WLessThan, type(block))
        self.assertEqual("49ABCDEF 12345678", str(block))

    def test_create_wequalto(self):
        block = Conditional32bitCodes.create(0x12345678, Conditions.EQUALTO, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(WEqualTo, type(block))
        self.assertEqual("59ABCDEF 12345678", str(block))

    def test_create_wnotequalto(self):
        block = Conditional32bitCodes.create(0x12345678, Conditions.NOTEQUALTO, 0x09ABCDEF)
        self.assertIsNotNone(block)
        self.assertEqual(WNotEqualTo, type(block))
        self.assertEqual("69ABCDEF 12345678", str(block))


class TestWGreaterThan(unittest.TestCase):
    FIRST = 0x30020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = WGreaterThan(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x0000000F", block.hex_value())

    def test_constructor_neg(self):
        WGreaterThan(0xFFFFFFFF, 0xFFFFFFF)
        WGreaterThan(0, 0)
        self.assertRaises(OutOfRangeError, WGreaterThan, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WGreaterThan, 0xFFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, WGreaterThan, 0x100000000, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WGreaterThan, 0xFFFFFFFF, 0x10000000)

    def test_parse(self):
        block = WGreaterThan.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(WGreaterThan, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x0000000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = WGreaterThan(0xF, 0x20200)
        self.assertEqual("assert(0x0000000F > *((int*)0x00020200 + offset));", block.to_c())
        self.assertEqual("assert(0x0000000F /* 15 */ > *((int*)0x00020200 + offset));", block.to_c(True))

    def test_to_human_readable(self):
        block = WGreaterThan(0xF, 0x20200)
        self.assertEqual("Assert that 0x0000000F > [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Assert that 0x0000000F(15) > [0x00020200 + offset]", block.to_human_readable(True))


class TestWLessThan(unittest.TestCase):
    FIRST = 0x40020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = WLessThan(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x0000000F", block.hex_value())

    def test_constructor_neg(self):
        WLessThan(0xFFFFFFFF, 0xFFFFFFF)
        WLessThan(0, 0)
        self.assertRaises(OutOfRangeError, WLessThan, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WLessThan, 0xFFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, WLessThan, 0x100000000, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WLessThan, 0xFFFFFFFF, 0x10000000)

    def test_parse(self):
        block = WLessThan.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(WLessThan, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x0000000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = WLessThan(0xF, 0x20200)
        self.assertEqual("assert(0x0000000F < *((int*)0x00020200 + offset));", block.to_c())
        self.assertEqual("assert(0x0000000F /* 15 */ < *((int*)0x00020200 + offset));", block.to_c(True))

    def test_to_human_readable(self):
        block = WLessThan(0xF, 0x20200)
        self.assertEqual("Assert that 0x0000000F < [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Assert that 0x0000000F(15) < [0x00020200 + offset]", block.to_human_readable(True))


class TestWEqualTo(unittest.TestCase):
    FIRST = 0x50020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = WEqualTo(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x0000000F", block.hex_value())

    def test_constructor_neg(self):
        WEqualTo(0xFFFFFFFF, 0xFFFFFFF)
        WEqualTo(0, 0)
        self.assertRaises(OutOfRangeError, WEqualTo, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WEqualTo, 0xFFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, WEqualTo, 0x100000000, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WEqualTo, 0xFFFFFFFF, 0x10000000)

    def test_parse(self):
        block = WEqualTo.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(WEqualTo, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x0000000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = WEqualTo(0xF, 0x20200)
        self.assertEqual("assert(0x0000000F == *((int*)0x00020200 + offset));", block.to_c())
        self.assertEqual("assert(0x0000000F /* 15 */ == *((int*)0x00020200 + offset));", block.to_c(True))

    def test_to_human_readable(self):
        block = WEqualTo(0xF, 0x20200)
        self.assertEqual("Assert that 0x0000000F == [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Assert that 0x0000000F(15) == [0x00020200 + offset]", block.to_human_readable(True))


class TestWNotEqualTo(unittest.TestCase):
    FIRST = 0x60020200
    SECOND = 0x0000000F

    def test_constructor(self):
        block = WNotEqualTo(0xF, 0x00020200)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x0000000F", block.hex_value())

    def test_constructor_neg(self):
        WNotEqualTo(0xFFFFFFFF, 0xFFFFFFF)
        WNotEqualTo(0, 0)
        self.assertRaises(OutOfRangeError, WNotEqualTo, -1, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WNotEqualTo, 0xFFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, WNotEqualTo, 0x100000000, 0xFFFFFFF)
        self.assertRaises(OutOfRangeError, WNotEqualTo, 0xFFFFFFFF, 0x10000000)

    def test_parse(self):
        block = WNotEqualTo.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(WNotEqualTo, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x0000000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = WNotEqualTo(0xF, 0x20200)
        self.assertEqual("assert(0x0000000F != *((int*)0x00020200 + offset));", block.to_c())
        self.assertEqual("assert(0x0000000F /* 15 */ != *((int*)0x00020200 + offset));", block.to_c(True))

    def test_to_human_readable(self):
        block = WNotEqualTo(0xF, 0x20200)
        self.assertEqual("Assert that 0x0000000F != [0x00020200 + offset]", block.to_human_readable())
        self.assertEqual("Assert that 0x0000000F(15) != [0x00020200 + offset]", block.to_human_readable(True))


class TestConditional16bitCodes(unittest.TestCase):

    def test_create_sgreaterthan(self):
        block = Conditional16bitCodes.create(0x5678, Conditions.GREATERTHAN, 0x09ABCDEF, 0x1234)
        self.assertIsNotNone(block)
        self.assertEqual(SGreaterThan, type(block))
        self.assertEqual("79ABCDEF 12345678", str(block))

    def test_create_slessthan(self):
        block = Conditional16bitCodes.create(0x5678, Conditions.LESSTHAN, 0x09ABCDEF, 0x1234)
        self.assertIsNotNone(block)
        self.assertEqual(SLessThan, type(block))
        self.assertEqual("89ABCDEF 12345678", str(block))

    def test_create_sequalto(self):
        block = Conditional16bitCodes.create(0x5678, Conditions.EQUALTO, 0x09ABCDEF, 0x1234)
        self.assertIsNotNone(block)
        self.assertEqual(SEqualTo, type(block))
        self.assertEqual("99ABCDEF 12345678", str(block))

    def test_create_snotequalto(self):
        block = Conditional16bitCodes.create(0x5678, Conditions.NOTEQUALTO, 0x09ABCDEF, 0x1234)
        self.assertIsNotNone(block)
        self.assertEqual(SNotEqualTo, type(block))
        self.assertEqual("A9ABCDEF 12345678", str(block))


class TestSGreaterThan(unittest.TestCase):
    FIRST = 0x70020200
    SECOND = 0x00AA000F

    def test_constructor(self):
        block = SGreaterThan(0xF, 0x00020200, 0xAA)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual(0xAA, block.mask)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x000F", block.hex_value())

    def test_constructor_neg(self):
        SGreaterThan(0xFFFF, 0xFFFFFFF, 0xFFFF)
        SGreaterThan(0, 0, 0)
        self.assertRaises(OutOfRangeError, SGreaterThan, -1, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SGreaterThan, 0xFFFF, -1, 0xFFFF)
        self.assertRaises(OutOfRangeError, SGreaterThan, 0xFFFF, 0xFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, SGreaterThan, 0x10000, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SGreaterThan, 0xFFFF, 0x10000000, 0xFFFF)
        self.assertRaises(OutOfRangeError, SGreaterThan, 0xFFFF, 0xFFFFFFF, 0x10000)

    def test_parse(self):
        block = SGreaterThan.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(SGreaterThan, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = SGreaterThan(0xF, 0x20200, 0xAA)
        self.assertEqual("assert(0x000F > (*((int*)0x00020200 + offset) & ~0x00AA);", block.to_c())
        self.assertEqual(
            "assert(0x000F /* 15 */ > (*((int*)0x00020200 + offset) & ~0x00AA /* 170 */);",
            block.to_c(True)
        )

    def test_to_human_readable(self):
        block = SGreaterThan(0xF, 0x20200, 0xAA)
        self.assertEqual("Assert that 0x000F > ([0x00020200 + offset] & ~0x00AA)", block.to_human_readable())
        self.assertEqual(
            "Assert that 0x000F(15) > ([0x00020200 + offset] & ~0x00AA(170))",
            block.to_human_readable(True)
        )


class TestSLessThan(unittest.TestCase):
    FIRST = 0x80020200
    SECOND = 0x00AA000F

    def test_constructor(self):
        block = SLessThan(0xF, 0x00020200, 0xAA)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual(0xAA, block.mask)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x000F", block.hex_value())

    def test_constructor_neg(self):
        SLessThan(0xFFFF, 0xFFFFFFF, 0xFFFF)
        SLessThan(0, 0, 0)
        self.assertRaises(OutOfRangeError, SLessThan, -1, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SLessThan, 0xFFFF, -1, 0xFFFF)
        self.assertRaises(OutOfRangeError, SLessThan, 0xFFFF, 0xFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, SLessThan, 0x10000, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SLessThan, 0xFFFF, 0x10000000, 0xFFFF)
        self.assertRaises(OutOfRangeError, SLessThan, 0xFFFF, 0xFFFFFFF, 0x10000)

    def test_parse(self):
        block = SLessThan.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(SLessThan, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = SLessThan(0xF, 0x20200, 0xAA)
        self.assertEqual("assert(0x000F < (*((int*)0x00020200 + offset) & ~0x00AA);", block.to_c())
        self.assertEqual(
            "assert(0x000F /* 15 */ < (*((int*)0x00020200 + offset) & ~0x00AA /* 170 */);",
            block.to_c(True)
        )

    def test_to_human_readable(self):
        block = SLessThan(0xF, 0x20200, 0xAA)
        self.assertEqual("Assert that 0x000F < ([0x00020200 + offset] & ~0x00AA)", block.to_human_readable())
        self.assertEqual(
            "Assert that 0x000F(15) < ([0x00020200 + offset] & ~0x00AA(170))",
            block.to_human_readable(True)
        )


class TestSEqualTo(unittest.TestCase):
    FIRST = 0x90020200
    SECOND = 0x00AA000F

    def test_constructor(self):
        block = SEqualTo(0xF, 0x00020200, 0xAA)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual(0xAA, block.mask)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x000F", block.hex_value())

    def test_constructor_neg(self):
        SEqualTo(0xFFFF, 0xFFFFFFF, 0xFFFF)
        SEqualTo(0, 0, 0)
        self.assertRaises(OutOfRangeError, SEqualTo, -1, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SEqualTo, 0xFFFF, -1, 0xFFFF)
        self.assertRaises(OutOfRangeError, SEqualTo, 0xFFFF, 0xFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, SEqualTo, 0x10000, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SEqualTo, 0xFFFF, 0x10000000, 0xFFFF)
        self.assertRaises(OutOfRangeError, SEqualTo, 0xFFFF, 0xFFFFFFF, 0x10000)

    def test_parse(self):
        block = SEqualTo.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(SEqualTo, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = SEqualTo(0xF, 0x20200, 0xAA)
        self.assertEqual("assert(0x000F == (*((int*)0x00020200 + offset) & ~0x00AA);", block.to_c())
        self.assertEqual(
            "assert(0x000F /* 15 */ == (*((int*)0x00020200 + offset) & ~0x00AA /* 170 */);",
            block.to_c(True)
        )

    def test_to_human_readable(self):
        block = SEqualTo(0xF, 0x20200, 0xAA)
        self.assertEqual("Assert that 0x000F == ([0x00020200 + offset] & ~0x00AA)", block.to_human_readable())
        self.assertEqual(
            "Assert that 0x000F(15) == ([0x00020200 + offset] & ~0x00AA(170))",
            block.to_human_readable(True)
        )


class TestSNotEqualTo(unittest.TestCase):
    FIRST = 0xA0020200
    SECOND = 0x00AA000F

    def test_constructor(self):
        block = SNotEqualTo(0xF, 0x00020200, 0xAA)
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0x20200, block.address)
        self.assertEqual(0xF, block.value)
        self.assertEqual(0xAA, block.mask)
        self.assertEqual("0x00020200", block.hex_address())
        self.assertEqual("0x000F", block.hex_value())

    def test_constructor_neg(self):
        SNotEqualTo(0xFFFF, 0xFFFFFFF, 0xFFFF)
        SNotEqualTo(0, 0, 0)
        self.assertRaises(OutOfRangeError, SNotEqualTo, -1, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SNotEqualTo, 0xFFFF, -1, 0xFFFF)
        self.assertRaises(OutOfRangeError, SNotEqualTo, 0xFFFF, 0xFFFFFFF, -1)
        self.assertRaises(OutOfRangeError, SNotEqualTo, 0x10000, 0xFFFFFFF, 0xFFFF)
        self.assertRaises(OutOfRangeError, SNotEqualTo, 0xFFFF, 0x10000000, 0xFFFF)
        self.assertRaises(OutOfRangeError, SNotEqualTo, 0xFFFF, 0xFFFFFFF, 0x10000)

    def test_parse(self):
        block = SNotEqualTo.parse(f"{self.FIRST:08X}", f"{self.SECOND:08X}")
        self.assertIsNotNone(block)
        self.assertEqual(SNotEqualTo, type(block))
        self.assertEqual(f"{self.FIRST:08X} {self.SECOND:08X}", str(block))
        self.assertEqual(0xF, block.value)
        self.assertEqual(0x20200, block.address)
        self.assertEqual("0x000F", block.hex_value())
        self.assertEqual("0x00020200", block.hex_address())

    def test_to_c(self):
        block = SNotEqualTo(0xF, 0x20200, 0xAA)
        self.assertEqual("assert(0x000F != (*((int*)0x00020200 + offset) & ~0x00AA);", block.to_c())
        self.assertEqual(
            "assert(0x000F /* 15 */ != (*((int*)0x00020200 + offset) & ~0x00AA /* 170 */);",
            block.to_c(True)
        )

    def test_to_human_readable(self):
        block = SNotEqualTo(0xF, 0x20200, 0xAA)
        self.assertEqual("Assert that 0x000F != ([0x00020200 + offset] & ~0x00AA)", block.to_human_readable())
        self.assertEqual(
            "Assert that 0x000F(15) != ([0x00020200 + offset] & ~0x00AA(170))",
            block.to_human_readable(True)
        )


if __name__ == '__main__':
    unittest.main()
