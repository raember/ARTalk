import enum
from abc import ABC
from typing import Optional, List

# https://web.archive.org/web/20170218053432/http://doc.kodewerx.org/hacking_nds.html
# https://github.com/JourneyOver/CTRPF-AR-CHEAT-CODES/blob/master/ActionReplayCodeTypes.txt

DXDATA_LABEL = 'DxDATA'


class Block:
    first: str
    second: str
    FIRST_REGEX: str
    SECOND_REGEX: str

    def __init__(self, first: str = None, second: str = None):
        if first is not None and second is not None:
            self.first = first
            self.second = second

    @classmethod
    def parse(cls, first: str, second: str) -> Optional[object]:
        pass

    def to_human_readable(self, comments=False):
        raise NotImplementedError("Must override!")

    def to_c(self, comments=False) -> str:
        raise NotImplementedError("Must override!")

    def _set_blocks(self):
        raise NotImplementedError("Must override!")

    def __str__(self):
        return f"{self.first} {self.second}"


class Offset:
    OFFSET_LABEL = 'offset'


class Address(Offset):
    ADDRESS_FORMAT = '#010X'
    address: int

    def hex_address(self, offset=False) -> str:
        return '0x' + f"{self.address:{self.ADDRESS_FORMAT}}"[2:] + (f" + {self.OFFSET_LABEL}" if offset else "")


class OutOfRangeError(BaseException):
    def __init__(self, attribute: str, low: int, high: int, actual: int):
        self.attribute = attribute
        self.low = low
        self.high = high
        self.actual = actual

    def __str__(self):
        return f"{self.attribute} should be between {self.low:08X} and {self.high:08X} but was {self.actual:08X}."


class Value:
    VALUE_FORMAT: str
    VALUE_NAME: str
    value: int

    def hex_value(self, decimal=False, c_style=False) -> str:
        suffix = ""
        if decimal:
            if c_style:
                suffix = f" /* {self.value} */"
            else:
                suffix = f"({self.value})"
        return '0x' + f"{self.value:{self.VALUE_FORMAT}}" + suffix


class Word(Value):
    VALUE_FORMAT = '08X'
    VALUE_NAME = 'word'


class Short(Value):
    VALUE_FORMAT = '04X'
    VALUE_NAME = 'short'


class Byte(Value):
    VALUE_FORMAT = '02X'
    VALUE_NAME = 'byte'


class Mask:
    MASK_FORMAT = '04X'
    mask: int

    def hex_mask(self, decimal=False, c_style=False) -> str:
        suffix = ""
        if decimal:
            if c_style:
                suffix = f" /* {self.mask} */"
            else:
                suffix = f"({self.mask})"
        return '0x' + f"{self.mask:{self.MASK_FORMAT}}" + suffix


class MemoryWrite(Value, Address, Block, ABC):
    def __init__(self, value: int = None, address: int = None):
        if value is not None and address is not None:
            self.value = value
            self.address = address
            self._set_blocks()
            super(MemoryWrite, self).__init__(self.first, self.second)
        super(MemoryWrite, self).__init__()

    @classmethod
    def create(cls, value: int, address: int) -> Block:
        if value <= 0xFF:
            return BWrite(value, address)
        if value <= 0xFFFF:
            return SWrite(value, address)
        return WWrite(value, address)

    def to_human_readable(self, comments=False):
        return f"Write {self.VALUE_NAME} {self.hex_value(comments)} to [{self.hex_address(True)}]"

    def to_c(self, comments=False):
        return f"*((int*){self.hex_address(True)}) = {self.hex_value(comments, True)};"


class WWrite(MemoryWrite, Word):
    @classmethod
    def parse(cls, first: str, second: str) -> Optional[Block]:
        if first[0] == "0":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return WWrite(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFFFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFFFFFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"0{self.address:07X}"
        self.second = f"{self.value:08X}"


class SWrite(MemoryWrite, Short):
    @classmethod
    def parse(cls, first: str, second: str) -> Optional[Block]:
        if first[0] == "1" and second[:4] == "0000":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return SWrite(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"1{self.address:07X}"
        self.second = f"{self.value:08X}"


class BWrite(MemoryWrite, Byte):
    @classmethod
    def parse(cls, first: str, second: str) -> Optional[Block]:
        if first[0] == "2" and second[:6] == "000000":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return BWrite(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFF:
            raise OutOfRangeError("Value", 0, 0xFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"2{self.address:07X}"
        self.second = f"{self.value:08X}"


class Conditions(enum.Enum):
    LESSTHAN = '<'
    GREATERTHAN = '>'
    EQUALTO = '=='
    NOTEQUALTO = '!='


class Conditional32bitCodes(Word, Address, Block, ABC):
    condition: Conditions

    def __init__(self, value: int = None, address: int = None):
        if value is not None and address is not None:
            self.value = value
            self.address = address
            self._set_blocks()
            super(Conditional32bitCodes, self).__init__(self.first, self.second)
        super(Conditional32bitCodes, self).__init__()

    @classmethod
    def create(cls, value: int, condition: Conditions, address: int) -> Block:
        if value > 0xFFFFFFFF or address > 0xFFFFFFFF:
            raise Exception("Value/address cannot be greater than 0xFFFFFFFF.")
        if condition == Conditions.LESSTHAN:
            return WLessThan(value, address)
        if condition == Conditions.GREATERTHAN:
            return WGreaterThan(value, address)
        if condition == Conditions.EQUALTO:
            return WEqualTo(value, address)
        if condition == Conditions.NOTEQUALTO:
            return WNotEqualTo(value, address)
        raise Exception(f"Unknown condition {condition}.")

    def to_human_readable(self, comments=False):
        return f"Assert that {self.hex_value(comments)} {self.condition.value} [{self.hex_address(True)}]"

    def to_c(self, comments=False):
        return f"assert({self.hex_value(comments, True)} {self.condition.value} *((int*){self.hex_address(True)}));"


class WGreaterThan(Conditional32bitCodes):
    condition = Conditions.GREATERTHAN

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "3":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return WGreaterThan(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFFFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFFFFFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"3{self.address:07X}"
        self.second = f"{self.value:08X}"


class WLessThan(Conditional32bitCodes):
    condition = Conditions.LESSTHAN

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "4":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return WLessThan(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFFFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFFFFFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"4{self.address:07X}"
        self.second = f"{self.value:08X}"
        return None


class WEqualTo(Conditional32bitCodes):
    condition = Conditions.EQUALTO

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "5":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return WEqualTo(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFFFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFFFFFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"5{self.address:07X}"
        self.second = f"{self.value:08X}"
        return None


class WNotEqualTo(Conditional32bitCodes):
    condition = Conditions.NOTEQUALTO

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "6":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second, 0)
            return WNotEqualTo(value, address)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFFFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFFFFFF, self.value)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"6{self.address:07X}"
        self.second = f"{self.value:08X}"
        return None


class Conditional16bitCodes(Short, Mask, Address, Block, ABC):
    condition: Conditions

    def __init__(self, value: int = None, address: int = None, mask: int = None):
        if value is not None and address is not None and mask is not None:
            self.value = value
            self.address = address
            self.mask = mask
            self._set_blocks()
            super(Conditional16bitCodes, self).__init__(self.first, self.second)
        super(Conditional16bitCodes, self).__init__()

    @classmethod
    def create(cls, value: int, condition: Conditions, address: int, mask: int) -> Block:
        if condition == Conditions.GREATERTHAN:
            return SGreaterThan(value, address, mask)
        if condition == Conditions.LESSTHAN:
            return SLessThan(value, address, mask)
        if condition == Conditions.EQUALTO:
            return SEqualTo(value, address, mask)
        if condition == Conditions.NOTEQUALTO:
            return SNotEqualTo(value, address, mask)
        raise Exception(f"Unknown condition {condition}.")

    def to_human_readable(self, comments=False):
        return f"Assert that {self.hex_value(comments)} " \
            f"{self.condition.value} ([{self.hex_address(True)}] & ~{self.hex_mask(comments)})"

    def to_c(self, comments=False):
        return f"assert({self.hex_value(comments, True)} " \
            f"{self.condition.value} (*((int*){self.hex_address(True)}) & ~{self.hex_mask(comments, True)});"


class SGreaterThan(Conditional16bitCodes):
    condition = Conditions.GREATERTHAN

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "7":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second[4:], 0)
            mask = int("0x" + second[:4], 0)
            return SGreaterThan(value, address, mask)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFF, self.value)
        if self.mask < 0 or self.mask > 0xFFFF:
            raise OutOfRangeError("Mask", 0, 0xFFFF, self.mask)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"7{self.address:07X}"
        self.second = f"{self.mask:04X}{self.value:04X}"
        return None


class SLessThan(Conditional16bitCodes):
    condition = Conditions.LESSTHAN

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "8":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second[4:], 0)
            mask = int("0x" + second[:4], 0)
            return SLessThan(value, address, mask)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFF, self.value)
        if self.mask < 0 or self.mask > 0xFFFF:
            raise OutOfRangeError("Mask", 0, 0xFFFF, self.mask)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"8{self.address:07X}"
        self.second = f"{self.mask:04X}{self.value:04X}"
        return None


class SEqualTo(Conditional16bitCodes):
    condition = Conditions.EQUALTO

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "9":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second[4:], 0)
            mask = int("0x" + second[:4], 0)
            return SEqualTo(value, address, mask)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFF, self.value)
        if self.mask < 0 or self.mask > 0xFFFF:
            raise OutOfRangeError("Mask", 0, 0xFFFF, self.mask)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"9{self.address:07X}"
        self.second = f"{self.mask:04X}{self.value:04X}"
        return None


class SNotEqualTo(Conditional16bitCodes):
    condition = Conditions.NOTEQUALTO

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if first[0] == "A":
            address = int("0x" + first[1:], 0)
            value = int("0x" + second[4:], 0)
            mask = int("0x" + second[:4], 0)
            return SNotEqualTo(value, address, mask)
        return None

    def _set_blocks(self):
        if self.value < 0 or self.value > 0xFFFF:
            raise OutOfRangeError("Value", 0, 0xFFFF, self.value)
        if self.mask < 0 or self.mask > 0xFFFF:
            raise OutOfRangeError("Mask", 0, 0xFFFF, self.mask)
        if self.address < 0 or self.address > 0xFFFFFFF:
            raise OutOfRangeError("Address", 0, 0xFFFFFFF, self.address)
        self.first = f"A{self.address:07X}"
        self.second = f"{self.mask:04X}{self.value:04X}"
        return None


class LoadOffset(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first[0] == "B" and cls.second == "00000000":
            cls.address = int("0x" + cls.first[1:], 0)
            return cls
        return None

    def __str__(self):
        return f"{self.OFFSET_LABEL} = *{self.hex_address()}"


class Repeat(Word, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "C0000000":
            cls.value = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"for 0..{self.hex_value(True)}:"


class ConditionEnd(Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D0000000" and cls.second == "00000000":
            return cls
        return None

    def __str__(self):
        return "fi"


class RepetitionEnd(Word, Offset, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D1000000":
            cls.value = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"Done; {self.OFFSET_LABEL} += {self.hex_value(True)}"


class Reset(Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D2000000" and cls.second == "00000000":
            return cls
        return None

    def __str__(self):
        return "Reset"


class SetOffset(Word, Offset, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D3000000":
            cls.value = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"{self.OFFSET_LABEL} = {self.hex_value()}"


class AddToDxData(Word, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D4000000":
            cls.value = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*{DXDATA_LABEL} += {self.hex_value(True)}"


class SetDxData(Word, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D5000000":
            cls.value = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*{DXDATA_LABEL} = {self.hex_value(True)}"


class DxDataWordWrite(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D6000000":
            cls.address = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*{DXDATA_LABEL} = word *({self.hex_address(True)})"


class DxDataShortWrite(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D7000000":
            cls.address = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*{DXDATA_LABEL} = short *({self.hex_address(True)})"


class DxDataByteWrite(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D8000000":
            cls.address = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*{DXDATA_LABEL} = byte *({self.hex_address(True)})"


class DxDataWordRead(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "D9000000":
            cls.address = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*({self.hex_address(True)}) = word *{DXDATA_LABEL}; {self.OFFSET_LABEL} += 4"


class DxDataShortRead(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "DA000000":
            cls.address = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*({self.hex_address(True)}) = short *{DXDATA_LABEL}; {self.OFFSET_LABEL} += 2"


class DxDataByteRead(Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "DB000000":
            cls.address = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"*({self.hex_address(True)}) = byte *{DXDATA_LABEL}; {self.OFFSET_LABEL} ++"


class AddToOffset(Word, Offset, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first == "DC000000":
            cls.value = int("0x" + cls.second, 0)
            return cls
        return None

    def __str__(self):
        return f"{self.OFFSET_LABEL} += *{self.hex_value()}"


class WaitForButton(Block):
    buttons: List[str]

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        cls.buttons = []
        if cls.first == "DD000000" and cls.second != "00000000":
            btn_code = int("0x" + cls.second, 0)
            if btn_code & 0x1:
                cls.buttons.append("A")
                btn_code -= 0x1
            if btn_code & 0x2:
                cls.buttons.append("B")
                btn_code -= 0x2
            if btn_code & 0x4:
                cls.buttons.append("SELECT")
                btn_code -= 0x4
            if btn_code & 0x8:
                cls.buttons.append("START")
                btn_code -= 0x8
            if btn_code & 0x10:
                cls.buttons.append("RIGHT")
                btn_code -= 0x10
            if btn_code & 0x20:
                cls.buttons.append("LEFT")
                btn_code -= 0x20
            if btn_code & 0x40:
                cls.buttons.append("UP")
                btn_code -= 0x40
            if btn_code & 0x80:
                cls.buttons.append("DOWN")
                btn_code -= 0x80
            if btn_code & 0x100:
                cls.buttons.append("R")
                btn_code -= 0x100
            if btn_code & 0x200:
                cls.buttons.append("L")
                btn_code -= 0x200
            if btn_code & 0x400:
                cls.buttons.append("X")
                btn_code -= 0x400
            if btn_code & 0x800:
                cls.buttons.append("Y")
                btn_code -= 0x800
            if btn_code & 0x2000:
                cls.buttons.append("DEBUG")
                btn_code -= 0x2000
            if btn_code & 0x8000:
                cls.buttons.append("NOT-FOLDED")
                btn_code -= 0x8000
            if btn_code == 0:
                return cls
        return None

    def __str__(self):
        return f"On {str.join(' + ', self.buttons)}:"


class Patch(Address, Block):
    value: int
    bytes: str

    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first[0] == "E":
            cls.value = int("0x" + cls.second, 0)
            cls.address = int("0x" + cls.first[1:], 0)
            cls.bytes = ""
            return cls
        return None

    def consume(self, bytestr: str) -> str:
        if len(self.bytes) == self.value:
            return bytestr
        while len(self.bytes) < self.value:
            self.bytes += bytestr[0]
            bytestr = bytestr[1:]
            if len(self.bytes) == self.value:
                return bytestr
        return bytestr

    def __str__(self):
        formatted_bytes = str.join(' ', [self.bytes[i:i + 8] for i in range(0, len(self.bytes), 8)])
        return f"Copy 0x{formatted_bytes}({self.value} bytes) to {self.hex_address(True)}"


class Memory(Word, Address, Block):
    @classmethod
    def parse(cls, first="", second="") -> Optional[Block]:
        if cls.first[0] == "F":
            cls.value = int("0x" + cls.second, 0)
            cls.address = int("0x" + cls.first[1:], 0)
            return cls
        return None

    def __str__(self):
        return f"Copy {self.value} bytes from {self.OFFSET_LABEL} to {self.hex_address()}"
