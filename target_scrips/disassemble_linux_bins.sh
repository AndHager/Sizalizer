#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=~/riscv_base/bin
OUT_PATH=${SCRIPT_ROOT}/../out

cp ${SCRIPT_ROOT}/../../linux-6.8.9/build_clang/vmlinux ${OUT_PATH}/vmlinux_clang
cp ${SCRIPT_ROOT}/../../linux-6.8.9/build_gcc/vmlinux ${OUT_PATH}/vmlinux_gcc

cd ${OUT_PATH}

${TOOL_PATH}/llvm-objdump -r -M no-aliases -d vmlinux_clang 1> ${OUT_PATH}/vmlinux_clang.asm
${TOOL_PATH}/llvm-objdump -r -M no-aliases -d vmlinux_gcc 1> ${OUT_PATH}/vmlinux_gcc.asm

# ${TOOL_PATH}/llvm-objdump -d libc.a 1> ${SCRIPT_ROOT}/out/libc.a.asm

cd ${SCRIPT_ROOT}
