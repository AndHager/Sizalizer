#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EMBENCH_DIR="${SCRIPT_ROOT}/../embench-iot"
BUILD_DIR="${EMBENCH_DIR}/../build"
LOG_DIR="${EMBENCH_DIR}/../log"

RISCV_ARCH="rv32imac_zcmp"
RISCV_ABI="ilp32"

cd "$EMBENCH_DIR"

# Build benchmarks
python3 ./build_all.py \
            --clean \
            --verbose \
            --arch=riscv32 \
            --chip=generic \
            --board=ri5cyverilator \
            --cc=/home/ahc/riscv/bin/clang \
            --ld=/home/ahc/riscv/bin/ld.lld \
            --cflags="-Oz -march=${RISCV_ARCH} -mabi=${RISCV_ABI} -fno-builtin-bcmp -mllvm -print-after=riscv-make-compressible -mllvm -debug-pass=Structure" \
            --ldflags="-march=${RISCV_ARCH} -mabi=${RISCV_ABI} -nostdlib" \
            --dummy-libs="crt0 libc libgcc libm"

cd "$SCRIPT_ROOT"
