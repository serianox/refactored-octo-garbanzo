#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ins import InstructionImmediateNode, InstructionImplicitNode

BYTE_TO_CONDITION = {
    0x00 << 5: "always",
    0x01 << 5: "overflow",
    0x02 << 5: "zero",
    0x03 << 5: "non-zero",
    0x04 << 5: "high",
    0x05 << 5: "safe",
}

BYTE_TO_MNEMONIC = {
    0x00: "halt",
    0x01: "noop",
    0x02: "push$",
    0x03: "load$",
    0x04: "store$",
    0x05: "xchg$",
    0x06: "dup",
    0x07: "dupn$",
    0x08: "swap",
    0x09: "pop",
    0x0a: "jump",
    0x0b: "jump$",
    0x0c: "link$",
    0x0d: "spawn",
    0x0e: "add",
    0x0f: "add$",
    0x10: "sub",
    0x11: "sub$",
    0x12: "mul",
    0x13: "mul$",
    0x14: "div",
    0x15: "div$",
    0x16: "mod",
    0x17: "mdd$",
    0x18: "neg",
    0x19: "not",
    0x1a: "and",
    0x1b: "and$",
    0x1c: "or",
    0x1d: "or$",
    0x1e: "xor",
    0x1f: "xor̀$",
}

def disassemble_one(memory, offset = 0):
    bytecode = memory[offset]
    condition = BYTE_TO_CONDITION[bytecode & 0xe0]
    mnemonic = BYTE_TO_MNEMONIC[bytecode & 0x1f]
    if (mnemonic.endswith("$")):
        mnemonic = mnemonic[:-1]
        if (memory[offset + 1] & 0x80 == 0x80):
            immediate = (memory[offset + 1] & 0x7f) << 8
            immediate += memory[offset + 2]
        else:
            immediate = memory[offset + 1]
        immediate = (immediate >> 1) ^ -(immediate & 1)
        return InstructionImmediateNode(condition, mnemonic, bytecode, immediate)
    else:
        return InstructionImplicitNode(condition, mnemonic, bytecode)

def disassemble(memory, offset=0):
    ast = []

    while offset < len(memory):
        decoded_instruction = disassemble_one(memory, offset)
        ast.append(decoded_instruction)
        offset += decoded_instruction.size()

    return ast
