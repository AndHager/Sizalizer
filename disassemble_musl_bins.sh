#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=~/riscv/bin
OUT_PATH=${SCRIPT_ROOT}/out

cp ${SCRIPT_ROOT}/../musl-1.2.5/lib/libc.a ${OUT_PATH}

cd ${OUT_PATH}

${TOOL_PATH}/llvm-ar x libc.a

for file in *.o;
do 
    #echo "  INFO Executing: ${TOOL_PATH}/llvm-objdump -d ${SCRIPT_ROOT}/embench-iot/bd/install/bin/${file} &> ${SCRIPT_ROOT}/out/${file}.rv32"
    ${TOOL_PATH}/llvm-objdump -d ${file} 1> ${SCRIPT_ROOT}/out/${file}.asm
done

# ${TOOL_PATH}/llvm-objdump -d libc.a 1> ${SCRIPT_ROOT}/out/libc.a.asm

cd ${SCRIPT_ROOT}
