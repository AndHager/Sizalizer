#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MUSL_DIR="${SCRIPT_ROOT}/../../musl-1.2.5"

mv ${MUSL_DIR}/config.mak ${MUSL_DIR}/config.mak_old
cp ${SCRIPT_ROOT}/../res/config.mak.DFG_ANALYSIS ${MUSL_DIR}/config.mak

# Build musl with pass
cd "$MUSL_DIR"
make clean
make -j10
make clean

mv ${MUSL_DIR}/config.mak_old ${MUSL_DIR}/config.mak

cd "$SCRIPT_ROOT"
