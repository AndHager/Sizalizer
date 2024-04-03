#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=/opt/riscv/bin
OUT_DIR=${SCRIPT_ROOT}/out

cd ${SCRIPT_ROOT}/../musl-1.2.5/lib/

for file in *.a;
do 
    ar x $file
done

for file in *.o libc.so;
do 
    fqfp=${SCRIPT_ROOT}/../musl-1.2.5/lib/${file}
    
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

