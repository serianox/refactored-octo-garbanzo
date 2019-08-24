#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asm import assemble, parse, pretty_print
from disasm import disassemble

import argparse

def chunk(memory, length):
    return (memory[0 + offset: length + offset] for offset in range(0, len(memory), length))

def hexdump(memory):
    for y in chunk(memory, 16):
        print(" ".join('{:02x}'.format(x) for x in y))

if __name__ == "__main__":
    memory = bytearray(32)

    ast = parse("""
; infinite loop
jump:
safe.jump jump
safe.jump 0
safe.jump 1
safe.jump 63
safe.jump 64
safe.jump 256
safe.jump -1
safe.jump -63
safe.jump -64
safe.jump -256
safe.jump jump
safe.jump loop2
loop2:
    """)

    pretty_print(ast)

    assemble(ast, memory, 0)

    hexdump(memory)

    pretty_print(disassemble(memory))
