#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_PATH=~/riscv_base/bin
OUT_DIR=${SCRIPT_ROOT}/"$1"

cd "${OUT_DIR}"
ASM=$(printf  '%s ' *.asm)
cd "${SCRIPT_ROOT}"
python3 ${SCRIPT_ROOT}/analysis/static.py --path ${OUT_DIR} ${ASM}

