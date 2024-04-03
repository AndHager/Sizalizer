#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=/opt/riscv/bin

cd ${SCRIPT_ROOT}/../musl-1.2.5/lib/

for file in *;
do 
    #echo "  INFO Executing: ${TOOL_PATH}/llvm-objdump -d ${SCRIPT_ROOT}/embench-iot/bd/install/bin/${file} &> ${SCRIPT_ROOT}/out/${file}.rv32"
    ${TOOL_PATH}/llvm-objdump -d ${file} &> ${SCRIPT_ROOT}/out/${file}.rv32
done

cd ${SCRIPT_ROOT}
