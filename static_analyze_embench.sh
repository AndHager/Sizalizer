#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=/opt/riscv/bin
OUT_DIR=${SCRIPT_ROOT}/out

for file in aha-mont64 edn huffbench nettle-aes qrduino st matmult-int nettle-sha256 statemate crc32 minver nsichneu sglib-combined ud cubic nbody picojpeg slre wikisort;
do 
    fqfp=${SCRIPT_ROOT}/embench-iot/bd/install/bin/${file}
    ${TOOL_PATH}/riscv32-unknown-elf-readelf -S $fqfp &> ${OUT_DIR}/${file}_size.txt

    
    cd "${SCRIPT_ROOT}/out"
    ${TOOL_PATH}/llvm-objcopy -O binary --only-section=.text ${fqfp} ${OUT_DIR}/${file}_text.dmp 
    binwalk --high=0.9 --low=0.8 -c -E -J ${OUT_DIR}/${file}_text.dmp &> ${OUT_DIR}/${file}_ent.txt
    cd "${SCRIPT_ROOT}"

    # echo "${TOOL_PATH}/riscv32-unknown-elf-readelf -S $fqfp"
    ${TOOL_PATH}/riscv32-unknown-elf-readelf -S $fqfp &> ${OUT_DIR}/${file}_size.txt
done

cd "${OUT_DIR}"
ASM=$(printf  '%s ' *.rv32)
cd "${SCRIPT_ROOT}"
python3 ${SCRIPT_ROOT}/valyzer/analyze.py --path ${OUT_DIR} ${ASM}

