import re
from typing import List, Optional

from artalk.codeblocks import Block, Patch, WWrite, SWrite, BWrite, WGreaterThan, WLessThan, \
    WEqualTo, WNotEqualTo, SGreaterThan, SLessThan, SEqualTo, SNotEqualTo, LoadOffset, Repeat, \
    ConditionEnd, RepetitionEnd, Reset, SetOffset1, AddToDxData, SetDxData, DxDataWordWrite, DxDataShortWrite, \
    DxDataByteWrite, DxDataWordRead, DxDataShortRead, DxDataByteRead, AddToOffset, WaitForButton, Memory


class BlockFactory:
    BLOCK = r"([0-9A-F]{8})\s*([0-9A-F]{8})"

    def can_create_block_from(self, line: str) -> Block:
        line = line.strip().upper()
        return re.compile(self.BLOCK).match(line.strip()) is not None

    def create_block(self, line: str, previous: Block = None) -> Optional[Block]:
        line = line.strip().upper()
        mtch = re.compile(self.BLOCK).match(line)
        first = mtch.group(1)
        second = mtch.group(2)
        if type(previous) == Patch and len(previous.bytes) < previous.value:
            remainder = previous.consume(first + second)
            if remainder.strip("0F") != "":  # Done reading bytes but the remainder isn't 0's or F's
                print(f"Remaining bytes after patch: {remainder}")
            return None
        possible_blocks = [
            WWrite,
            SWrite,
            BWrite,
            WLessThan,
            WGreaterThan,
            WEqualTo,
            WNotEqualTo,
            SGreaterThan,
            SLessThan,
            SEqualTo,
            SNotEqualTo,
            LoadOffset,
            Repeat,
            ConditionEnd,
            RepetitionEnd,
            Reset,
            SetOffset1,
            AddToDxData,
            SetDxData,
            DxDataWordWrite,
            DxDataShortWrite,
            DxDataByteWrite,
            DxDataWordRead,
            DxDataShortRead,
            DxDataByteRead,
            AddToOffset,
            WaitForButton,
            Patch,
            Memory
        ]
        for block in possible_blocks:
            obj = block.parse(first, second)
            if obj is not None:
                return obj
        raise Exception(f"No matching block pattern found: \"{line}\"")


class Code:
    CODE_HEAD = r"\[(.+)\]"

    title: str
    blocks: List[Block]
    factory: BlockFactory

    def __init__(self, line: str = ""):
        self.blocks = []
        self.title = ""
        self.factory = BlockFactory()
        if line != "":
            self.title = re.compile(self.CODE_HEAD).match(line.strip()).group(1)

    def parse_block(self, line: str) -> Block:
        if not self.factory.can_create_block_from(line):
            raise Exception(f"Line doesn't match expected code block layout: \"{line}\"")
        previous = None
        if len(self.blocks) > 0:
            previous = self.blocks[-1]
        block = self.factory.create_block(line, previous)
        if block is not None:
            self.blocks.append(block)
        return block

    @classmethod
    def is_title(cls, line: str) -> bool:
        return re.compile(cls.CODE_HEAD).match(line.strip()) is not None

    def __str__(self):
        if self.title != "":
            return self.title
        return super(Code, self).__str__()


class Parser:
    codes: List[Code]

    def parse(self, string: str) -> List[Code]:
        self.codes = []
        code = None
        for line in string.splitlines():
            line = line.strip()
            if len(self.codes) == 0:  # Look for first code
                if Code.is_title(line):
                    code = Code(line)
                    self.codes.append(code)
                continue
            if len(line) != 0 and len(code.blocks) == 0:  # Title read, no blocks yet
                code.parse_block(line)
                continue
            if len(line) != 0:  # Title and at least one block read
                if Code.is_title(line):  # New code encountered
                    code = Code(line)
                    self.codes.append(code)
                else:  # Still reading code blocks
                    code.parse_block(line)
        return self.codes
