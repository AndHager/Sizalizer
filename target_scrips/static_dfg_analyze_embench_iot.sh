#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EMBENCH_DIR="${SCRIPT_ROOT}/embench-iot"
BUILD_DIR="${EMBENCH_DIR}/build"
LOG_DIR="${EMBENCH_DIR}/log"

cd "$EMBENCH_DIR"

# Build benchmarks with pass
python3 ./build_all.py \
            --clean \
            --verbose \
            --arch=riscv32 \
            --chip=generic \
            --board=ri5cyverilator \
            --cc=clang \
            --cflags="-fno-builtin-bcmp -Oz -fpass-plugin=./seal/llvm-pass-plugin/build/libLLVMCDFG.so" \
            --ldflags="-nostartfiles -nostdlib" \
            --dummy-libs="crt0 libc libgcc libm"

cd "$SCRIPT_ROOT"
