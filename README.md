<!--# Title-->

The final name of the game should be a horrible French pun, like every French project. :)

## Rules

### Last Thread Standing

### Capture the Blob

### King of the Heap

## Core Architecture

### Stack

The stack is a LIFO structure that can store 16 bits two's complements values.

The stack size is configurable but should not exceed 16 elements.

Stack underflow or overflow is an error and triggers a [fault](#fault).

### Instruction Pointer

The instruction pointer is a 16 bit register that holds the offset of the next instruction to execute by the core.

## Memory

The memory is organized in a single contiguous adressable list of cells. The memory address wraps around, both in positive and negative overflow.

A cell can store a single 8-bits two's complement value.

The memory size is configurable, but should not exceed 64Ki cells.

### Protection

Memory cells can be protected by a policy loosely based on Discretionary Access Control (DAC). A cell can be assigned a single user owner and read, write or execute permissions for this user and other users.

The memory protection allows to shape the memory to prevent users from inadvertently trashing it.

Performing unauthorized memory access triggers a [fault](#fault).

Unauthorizer memory access are:
- attempting to read/write/execute a cell owned by a user other than the current user whose read/write/execute policy for all users is set to no.
- attempting to read/write/execute a cell owned by the current user user whose read/write/execute policy for owner user is set to no.

Note that it is possible to execute a cell even when the read policy is set to no.

## Execution

### Thread

A thread is the set of a user ID, an instruction pointer and a stack.

A user does not necessarily looses the battle if it has no threads assigned to him.

### Scheduling

Threads are scheduled using the following rules:
- only one instructions is executed before yielding to the next threads,
- the next thread to be executed is chosen among the threads of the next user,
- the least recently executed thread is chosen.

It means that when a new thread is spawned, it will always be executed when the next thread from the same user is scheduled.

### Fault

When a fault occurs, the incriminated thread is eliminated, i.e. it is removed from the owner's list of threads.

## Assembly

### Grammar

```
line = [label] [instruction] [comment] eol
label = identifier ":"
instruction = [condition "."] mnemonic [digit | identifier]
comment = ";" /[^\n\r]/
condition = "always" | ...
mnemonic = "halt" | "test" | ...
identifier = /[a-z]+([-_][a-z]+)*/i
digit = binary | octal | decimal | hexadecimal
binary = /-?[0-1]+(_[0-1]+)*b/
octal = /-?[0-7_]+(_[0-7]+)*o/
decimal = /-?[0-9_]+(_[0-9]+)*d?/
hexadecimal = /-?[0-9a-f_]+(_[0-9a-f]+)*h/i
eol = "\n" | "\r" | "\n\r" | "\r\n"
```

### Examples

```
; infinite loop
label:
always.jump label
```

```
link sub
halt

sub:
jump
```

## Instruction Set

note: the value `00h` for uninitialized memory is the encoded value for the instruction `always.halt`.

### Summary

- `xxx0_0000b`: `halt`
- `xxx0_0001b`: `noop`
- `xxx0_0010b`: `push`
- `xxx0_0011b`: `load`
- `xxx0_0100b`: `store`
- `xxx0_0101b`: `xchg`
- `xxx0_0110b`: `dup`
- `xxx0_0111b`: `dupn`
- `xxx0_1000b`: `swap`
- `xxx0_1001b`: `pop`
- `xxx0_1010b`: `jump`
- `xxx0_1011b`: `jump`
- `xxx0_1100b`: `link`
- `xxx0_1101b`: `spawn`
- `xxx0_1110b`: `add`
- `xxx0_1111b`: `add`
- `xxx1_0000b`: `sub`
- `xxx1_0001b`: `sub`
- `xxx1_0010b`: `mul`
- `xxx1_0111b`: `mul`
- `xxx1_0100b`: `div`
- `xxx1_0101b`: `div`
- `xxx1_0110b`: `mod`
- `xxx1_1011b`: `mdd`
- `xxx1_1000b`: `neg`
- `xxx1_1001b`: `not`
- `xxx1_1010b`: `and`
- `xxx1_1011b`: `and`
- `xxx1_1100b`: `or`
- `xxx1_1101b`: `or`
- `xxx1_1110b`: `xor`
- `xxx1_1111b`: `xor̀`

### Conditional Execution

All instructions are conditionals, meaning they are skipped when the conditions are not met.

The following conditions are:
- `000x_xxxxb`: `always` the instruction will always be executed,
- `001x_xxxxb`: `overflow` the instruction will be executed only if the previous instruction caused an overflow,
- `010x_xxxxb`: `zero` the instruction will be executed only if the top of the stack is zero,
- `011x_xxxxb`: `non-zero` the instruction will be executed only if the top of the stack is not zero,
- `100x_xxxxb`: `positive` the instruction will be executed only if the top of the stack is positive,
- `101x_xxxxb`: `negative` the instruction will be executed only if the top of the stack is negative,
- `110x_xxxxb`: `high` the instruction will be executed only at least one of the top of the stack's high bits is not zero,
- `111x_xxxxb`: `safe` the instruction will not cause a [fault](#fault) but will skipped if it should have caused a fault

### Immediate Parameters

Most instruction allows to encore the second or only operand into next one or two cells.

Immediate values are encoded using ZigZag encoding and 16-bits Varint (see [[Protocol Buffers]](https://developers.google.com/protocol-buffers/docs/encoding)).

Encoding is done using the following formula:

```
(i >> 16-1) ^ (i << 1)
```

Decoding is done using the following formula:

```
(i >>> 1) ^ -(i & 1)
```

Examples:

```
  0 -> 0001h -> 0000h -> 0000_0000b
```

```
 -1 -> ffffh -> 0001h -> 0000_0001b
```

```
  1 -> 0001h -> 0002h -> 0000_0010b
```

```
 63 -> 003fh -> 007eh -> 0111_1110b
```

```
-63 -> ffc0h -> 007fh -> 0111_1111b
```

```
 64 -> 0080h -> 0100h -> 1000_0001b 0000_0000b
```


### Memory

#### Load

#### Store

### Stack

#### Dup

Duplicate the top element of the stack.

```
..., T -> ..., T, T
```

#### Dupn

Duplicate the nth element of the stack.

```
... -> ..., T
```

#### Swap

Pop the two topmost elements of the stack.

```
..., T, S -> ..., S, T
```

#### Pop

Pop the top element of the stack.

```
..., T -> ...
```

### Arithmetic

#### Add

Add the two topmost elements of the stack together, poping them and pushing the result on the stack.

- `xxx0_1110b`: `[condition.]add`
- `xxx0_1111b`: `[condition.]add <immediate value>`

```
..., T[, S] -> ...,  T + S
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Sub

Substract the two topmost elements of the stack together, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T - S
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Mul

Multiply the two topmost elements of the stack together, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T * S
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Div

Divide the two topmost elements of the stack together, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T / S
```

If the denominator is zero, this instruction triggers a [fault](#fault).

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Mod

Compute the remainder of the integer division the two topmost elements of the stack together, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T mod M
```

If the denominator is zero, this instruction triggers a [fault](#fault).

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Neg

Negate the topmost element of the stack.

```
...[, T] -> ..., -T
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

### Logic

#### Not

Logically negate the topmost element of the stack, inverting all bits.

```
...[, T] -> ..., ~T
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### And

Compute the logical and of the two topmost elements of the stack, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T & S
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Or

Compute the logical or of the two topmost elements of the stack, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T | S
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

#### Xor

Compute the logical and of the two topmost elements of the stack, poping them and pushing the result on the stack.

```
..., T[, S] -> ..., T ^ S
```

In immediate mode, the top operand of the stack is replaced by the value encoded in the instruction.

### Control

note: Link and Jump with implicit operand should use absolute addressing, since Link could only work if it pushes absolute addresses on the stack.

#### Jump

Set the instruction pointer to a new value.

```
...[, T] -> ...
```

When the operand is explicit, the value of the operand is added to the current value of the instruction pointer to compute the new value of the instruction pointer.

When the operand is implicit, the value of the instruction pointer is set to the value of the operand.

#### Link

Set the instruction pointer to a new value and save the instruction pointer value of the instruction that should have been executed if the instruction pointer hadn't been updated.

```
..., T -> ..., S
```

#### Spawn

Spawn a new thread. The content of the stack is duplicated in the child thread. The owner of the child thread is set to the owner of the current thread.

```
... -> ...
```

The instruction pointer of the child thread is computed by adding the value of the operand to the value of the instruction pointer of the current thread. 

#### Halt

Halt the current thread. The thread is removed from its owner's list of threads.

```
..., T ->
```

#### Noop

This instruction does nothing, wasting one cycle.

```
... -> ...
```

### Pseudo-Instruction

#### Data

This pseudo-instruction allows to set a single cell to an arbitrary value.
