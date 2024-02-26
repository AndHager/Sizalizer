#!/bin/bash

set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build Static analysis pass
cd "${SCRIPT_ROOT}/seal/llvm-pass-plugin"
mkdir -p build
cd build
cmake ..
make -j4

# Build Embench
${SCRIPT_ROOT}/compile_embench_iot.sh 


cd "${SCRIPT_ROOT}"
