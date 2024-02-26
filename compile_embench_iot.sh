#!/bin/bash

set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EMBENCH_DIR="${SCRIPT_ROOT}/embench-iot"
BUILD_DIR="${EMBENCH_DIR}/build"
LOG_DIR="${EMBENCH_DIR}/log"

RISCV_ARCH="rv32gc"
RISCV_ABI="ilp32d"

cd "$EMBENCH_DIR"

# Build benchmarks
python3 ./build_all.py \
            --clean \
            --verbose \
            --arch=riscv32 \
            --chip=generic \
            --board=ri5cyverilator \
            --cc=/opt/riscv-elf/bin/clang \
            --cflags="-march=${RISCV_ARCH} -mabi=${RISCV_ABI} -fno-builtin-bcmp -Oz" \
            --ldflags="-march=${RISCV_ARCH} -mabi=${RISCV_ABI} -nostartfiles -nostdlib" \
            --dummy-libs="crt0 libc libgcc libm"

cd "$SCRIPT_ROOT"
