#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Node:
    def toAsm(self):
        pass

    def toBytes(self, bytearray, offset, labels):
        return offset + self.size()

    def computeOffset(self, offset):
        self.offset = offset
        return offset + self.size()

    def getOffset(self):
        return self.offset

    def addReference(self, list):
        return

    def size(self):
        pass

class LabelNode(Node):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Label: " + self.name

    def toAsm(self):
        return self.name + ":"

    def addReference(self, list):
        list[self.name] = self
        return

    def size(self):
        return 0

class CommentNode(Node):
    def __init__(self, text):
        self.text = text.strip()

    def __str__(self):
        return "Comment: " + self.text

    def toAsm(self):
        return "; " + self.text
        
    def size(self):
        return 0

class InstructionNode(Node):
    def encode(self):
        return 

class InstructionImplicitNode(InstructionNode):
    def __init__(self, condition, mnemonic, bytecode):
        self.condition = condition
        self.mnemonic = mnemonic
        self.bytecode = bytecode

    def __str__(self):
        return "Instruction: " + self.condition + "." + self.mnemonic

    def toAsm(self):
        return self.condition + "." + self.mnemonic

    def toBytes(self, bytearray, offset, labels):
        bytearray[offset] = self.bytecode
        return super().toBytes(bytearray, offset, labels)

    def size(self):
        return 1

class InstructionImmediateNode(InstructionNode):
    def __init__(self, condition, mnemonic, bytecode, immediate):
        self.condition = condition
        self.mnemonic = mnemonic
        self.immediate = immediate
        if type(immediate).__name__ == "int":
            self.encoded_immediate = self.encode_immediate(immediate)
        self.bytecode = bytecode

    @staticmethod
    def encode_immediate(immediate):
        return (immediate >> 16-1) ^ (immediate << 1)

    def __str__(self):
        return "Instruction: " + self.condition + "." + self.mnemonic + " " + str(self.immediate)

    def toAsm(self):
        return self.condition + "." + self.mnemonic + " " + str(self.immediate)

    def toBytes(self, bytearray, offset, labels):
        bytearray[offset] = self.bytecode

        if type(self.immediate).__name__ == "str":
            print(self.offset)
            print(labels[self.immediate].offset)
            self.immediate = labels[self.immediate].offset - self.offset
            self.encoded_immediate = self.encode_immediate(self.immediate)

        if type(self.immediate).__name__ == "str" or self.encoded_immediate > 0x7f:
            bytearray[offset+1] = (self.encoded_immediate >> 8) & 0xff | 0x80
            bytearray[offset+2] = self.encoded_immediate & 0xff
            return super().toBytes(bytearray, offset, labels)
        else:
            bytearray[offset+1] = self.encoded_immediate & 0xff
            return super().toBytes(bytearray, offset, labels)

    def size(self):
        if type(self.immediate).__name__ == "str" or self.encoded_immediate > 0x7f:
            return 3
        else:
            return 2

def label(name):
    return LabelNode(name)

def comment(text):
    return CommentNode(text)

CONDITION_TO_BYTE = {
    "always": 0x00 << 5,
    "overflow": 0x01 << 5,
    "zero": 0x02 << 5,
    "non-zero": 0x03 << 5,
    "high": 0x04 << 5,
    "safe": 0x05 << 5,
}

INSTRUCTION_TO_BYTE = {
    "halt": 0x00,
    "noop": 0x01,
    "push$": 0x02,
    "load$": 0x03,
    "store$": 0x04,
    "xchg$": 0x05,
    "dup": 0x06,
    "dupn$": 0x07,
    "swap": 0x08,
    "pop": 0x09,
    "jump": 0x0a,
    "jump$": 0x0b,
    "link$": 0x0c,
    "spawn": 0x0d,
    "add": 0x0e,
    "add$": 0x0f,
    "sub": 0x10,
    "sub$": 0x11,
    "mul": 0x12,
    "mul$": 0x13,
    "div": 0x14,
    "div$": 0x15,
    "mod": 0x16,
    "mdd$": 0x17,
    "neg": 0x18,
    "not": 0x19,
    "and": 0x1a,
    "and$": 0x1b,
    "or": 0x1c,
    "or$": 0x1d,
    "xor": 0x1e,
    "xor̀$": 0x1f,
}

def instruction(instruction):
    condition = instruction['condition']
    condition = condition or "always"

    mnemonic = instruction['mnemonic']
    operand = instruction['operand']

    has_operand = operand != None

    bytecode = CONDITION_TO_BYTE[condition] + INSTRUCTION_TO_BYTE[mnemonic + (has_operand and "$" or "")]

    if has_operand:
        return InstructionImmediateNode(condition, mnemonic, bytecode, operand)
    else:
        return InstructionImplicitNode(condition, mnemonic, bytecode)
