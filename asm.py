#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ins import comment, instruction, label

from parsy import eof, regex, seq, string, string_from
import re

eol = regex(r'(\n|\r|\n\r|\r\n)+')

ws = regex(r'\s*')

ws1 = regex(r'[ \t]+')

hexadecimal = regex(r'-?[0-9a-f_]+(_[0-9a-f]+)*h').map(lambda s: int(re.sub(r'[_h]', '', s), 16))

decimal = regex(r'-?[0-9_]+(_[0-9]+)*d?').map(lambda s: int(re.sub(r'[_d]', '', s)))

octal = regex(r'-?[0-7_]+(_[0-7]+)*o').map(lambda s: int(re.sub(r'[_o]', '', s), 8))

binary = regex(r'-?[0-1_]+(_[0-1]+)*b').map(lambda s: int(re.sub(r'[_b]', '', s), 2))

digit = binary | octal | decimal | hexadecimal

identifier = regex(r'[a-z][a-z0-9]*([-_][a-z0-9]+)*')

mnemonic = string_from("halt", "noop", "push", "load", "store", "xchg", "dup", "dupn", "swap", "pop", "jump", "link", "spawn", "add", "sub", "mul", "div", "mod", "neg", "not", "and", "or", "xor")

condition = string_from("always", "overflow", "zero", "non-zero", "positive", "negative", "high", "safe")

comment = (string(";") >> regex(r'[^\n\r]*') << (eol | eof)).map(comment)

instruction = seq(condition=(condition << string(".")).optional(), mnemonic=mnemonic, operand=(ws1 >> (digit | identifier)).optional()).map(instruction)

label = (identifier << string(":")).map(label)

statement = label | instruction | comment

lexer = ws >> statement.sep_by(ws) << (ws | eof)

def parse(stream):
    return lexer.parse(stream)

def assemble(ast, memory, offset=0):
    labels = {}
    for node in ast:
        node.addReference(labels)

    curren_offset = offset
    for node in ast:
        curren_offset = node.computeOffset(curren_offset)

    for node in ast:
        offset = node.toBytes(memory, offset, labels)
    
    return offset

def pretty_print(ast):
    for node in ast:
        print(node.toAsm())
