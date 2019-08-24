# -*- coding: utf-8 -*-

from asm import parse
import pytest

def test_empty():
    parse("")
    assert True

def test_label():
    res = parse("foo:")
    assert str(res[0]) == "Label: foo"

def test_mnemonic():
    res = parse("halt")
    assert str(res[0]) == "Instruction: always.halt"

def test_condition():
    res = parse("safe.halt")
    assert str(res[0]) == "Instruction: safe.halt"

def test_operand_label():
    res = parse("jump foo")
    assert str(res[0]) == "Instruction: always.jump foo"

def test_operand_binary():
    res = parse("jump 0101_0110b")
    assert str(res[0]) == "Instruction: always.jump 86"

def test_operand_octal():
    res = parse("jump 0770o")
    assert str(res[0]) == "Instruction: always.jump 504"

def test_operand_decimal():
    res = parse("jump -9999d")
    assert str(res[0]) == "Instruction: always.jump -9999"

def test_operand_hexadecimal():
    res = parse("jump deadbeefh")
    assert str(res[0]) == "Instruction: always.jump 3735928559"

def test_comment():
    res = parse("; foo")
    assert str(res[0]) == "Comment: foo"

def test_complete_line():
    res = parse("jump: always.jump jump ; jump")
    assert str(res[0]) == "Label: jump"
    assert str(res[1]) == "Instruction: always.jump jump"

def test_multiple_lines():
    parse("""
; infinite loop
label:
always.jump label
    """)
    assert True

def test_multiple_lines2():
    parse("""
link sub
halt

sub:
jump
    """)
    assert True
