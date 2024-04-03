#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MUSL_DIR="${SCRIPT_ROOT}/../musl-1.2.5"

cp ${SCRIPT_ROOT}/res/config.mak.RISCV_BUILD ${MUSL_DIR}/config.mak

# Build musl with pass
cd "$MUSL_DIR"
make clean
make -j11

cd "$SCRIPT_ROOT"
