#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=/opt/riscv/bin

for file in aha-mont64 edn huffbench nettle-aes qrduino st matmult-int nettle-sha256 statemate crc32 minver nsichneu sglib-combined ud cubic nbody picojpeg slre wikisort;
do 
    #echo "  INFO Executing: ${TOOL_PATH}/llvm-objdump -d ${SCRIPT_ROOT}/embench-iot/bd/install/bin/${file} &> ${SCRIPT_ROOT}/out/${file}.rv32"
    ${TOOL_PATH}/llvm-objdump -d ${SCRIPT_ROOT}/embench-iot/bd/install/bin/${file} &> ${SCRIPT_ROOT}/out/${file}.rv32
done
