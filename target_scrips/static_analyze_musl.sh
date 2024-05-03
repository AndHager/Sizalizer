#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=~/riscv/bin
OUT_DIR=${SCRIPT_ROOT}/../"$1"

# cd ${SCRIPT_ROOT}/../musl-1.2.5/lib/
# 
# if [ false ]; then
#     for file in *.o;
#     do 
#         fqfp=${SCRIPT_ROOT}/../musl-1.2.5/lib/${file}
#         
#         # cd "${SCRIPT_ROOT}/out"
#         # ${TOOL_PATH}/llvm-objcopy -O binary --only-section=.text ${fqfp} ${OUT_DIR}/${file}_text.dmp 
#         # binwalk --high=0.9 --low=0.8 -c -E -J ${OUT_DIR}/${file}_text.dmp &> ${OUT_DIR}/${file}_ent.txt
#         # cd "${SCRIPT_ROOT}"
# 
#         # echo "${TOOL_PATH}/riscv32-unknown-elf-readelf -S $fqfp"
#         ${TOOL_PATH}/riscv32-unknown-elf-readelf -S $fqfp &> ${OUT_DIR}/${file}_size.txt
#     done
# fi
# 
# ${TOOL_PATH}/riscv32-unknown-elf-readelf -S ${SCRIPT_ROOT}/../musl-1.2.5/lib/libc.a &> ${OUT_DIR}/libc.a_size.txt

cd "${OUT_DIR}"
ASM=$(printf  '%s ' *.asm)
cd "${SCRIPT_ROOT}"
python3 ${SCRIPT_ROOT}/../analysis/static.py --path ${OUT_DIR} ${ASM} &> ${OUT_DIR}/static_out.txt

