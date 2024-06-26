#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_DIR="~/riscv_base/bin"
LINUX_DIR="${SCRIPT_ROOT}/../../linux-6.8.9"
CONF_DIR="${LINUX_DIR}/arch/riscv/configs"

cd $LINUX_DIR
mv Makefile Makefile.old
cp $SCRIPT_ROOT/../res/LinuxMakefileCFG $LINUX_DIR/Makefile
cat $CONF_DIR/32-bit.config $CONF_DIR/defconfig > $CONF_DIR/32_defconfig

# Build with clang
make mrproper
make -j10 ARCH=riscv LLVM=1 CC=clang O=./build 32_defconfig
cd build
make -j10 ARCH=riscv LLVM=1 CC=clang

cd $LINUX_DIR
make mrproper
rm -r ./build
rm Makefile
mv Makefile.old Makefile

cd "$SCRIPT_ROOT"
