#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build Static analysis pass
cd "${SCRIPT_ROOT}/seal/llvm-pass-plugin"
mkdir -p build
cd build
cmake ..
make -j4

cd "${SCRIPT_ROOT}"
