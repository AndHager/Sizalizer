#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INTEGRATOR_PATH="${SCRIPT_ROOT}"/..
EMBENCH_PATH="${INTEGRATOR_PATH}/embench-iot"
BUILD_PATH="${EMBENCH_PATH}/bd/build"
SUPPORT_PATH="${EMBENCH_PATH}/support"
BD_SUPPORT_PATH="${EMBENCH_PATH}/bd/support"

CC="/home/ahc/riscv/bin/clang"
CFLAGS="-D__riscv__ -Oz -march=rv32imac_zcmp -mabi=ilp32 -fno-builtin-bcmp -I${SUPPORT_PATH} -I${EMBENCH_PATH}/config/riscv32/boards/ri5cyverilator -I${EMBENCH_PATH}/config/riscv32/chips/generic -I${EMBENCH_PATH}/config/riscv32 -DCPU_MHZ=1 -DWARMUP_HEAT=1"

if [[ "${1:-NONE}" == "clean" ]]; then
    rm -rf ${BUILD_PATH}
    rm -rf "${EMBENCH_PATH}/bd/install"
    exit
fi

# create build dir
cp -r ${INTEGRATOR_PATH}/res/* ${INTEGRATOR_PATH}/embench-iot/bd
cp -r ${EMBENCH_PATH}/src/* ${EMBENCH_PATH}/bd/src
cp -r ${EMBENCH_PATH}/support/* ${EMBENCH_PATH}/bd/support
cp -r ${EMBENCH_PATH}/config/* ${EMBENCH_PATH}/bd/config
mkdir -p ${BUILD_PATH}

# Build support Files for etiss
${CC} ${CFLAGS} -o ${BD_SUPPORT_PATH}/beebsc_etiss.o -c ${SUPPORT_PATH}/beebsc.c
${CC} ${CFLAGS} -o ${BD_SUPPORT_PATH}/main_etiss.o -c ${SUPPORT_PATH}/main.c
${CC} ${CFLAGS} -o ${BD_SUPPORT_PATH}/dummy-crt0_etiss.o -c ${SUPPORT_PATH}/dummy-crt0.c
${CC} ${CFLAGS} -o ${BD_SUPPORT_PATH}/dummy-libc_etiss.o -c ${SUPPORT_PATH}/dummy-libc.c
${CC} ${CFLAGS} -o ${BD_SUPPORT_PATH}/dummy-libgcc_etiss.o -c ${SUPPORT_PATH}/dummy-libgcc.c
${CC} ${CFLAGS} -o ${BD_SUPPORT_PATH}/dummy-libm_etiss.o -c ${SUPPORT_PATH}/dummy-libm.c

${CC} ${CFLAGS} -o ${EMBENCH_PATH}/bd/config/riscv32/chips/generic/chipsupport_etiss.o -c ${EMBENCH_PATH}/config/riscv32/chips/generic/chipsupport.c
${CC} ${CFLAGS} -o ${EMBENCH_PATH}/bd/config/riscv32/boards/ri5cyverilator/boardsupport_etiss.o -c ${EMBENCH_PATH}/config/riscv32/boards/ri5cyverilator/boardsupport.c

# Build embench-iot for etiss
cd ${BUILD_PATH}
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=rv32gc-toolchain.cmake -DRISCV_TOOLCHAIN_PREFIX=/opt/riscv -DCMAKE_INSTALL_PREFIX=../install ..
make VERBOSE=1
make install

cd "${SCRIPT_ROOT}"
