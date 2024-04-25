#!/bin/bash

# C to Object
/opt/riscv/bin/clang -S -emit-llvm hello.c -o hello.ll

# Generate dot cfg
# /opt/clang+llvm-17.0.2-x86_64-linux-gnu-ubuntu-22.04/bin/opt -p dot-cfg -disable-output hello.ll

# Object to not linked RISC-V assembly
/opt/riscv/bin/clang -emit-llvm -c hello.ll -o hello.s

# Assembly to Object
#/opt/riscv/bin/clang -c hello.o

# Object to Executable
/opt/riscv/bin/clang hello.o -o hello -fuse-ld=/opt/riscv/bin/ld.lld
