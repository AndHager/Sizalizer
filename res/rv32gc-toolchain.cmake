cmake_minimum_required(VERSION 3.10)


set(RISCV_ARCH "rv32gc" CACHE STRING "RISC-V architecture (-march)")
set(RISCV_ABI "ilp32d" CACHE STRING "RISC-V ABI (-mabi)")

set(RISCV_TOOLCHAIN_PREFIX "" CACHE STRING "optional prefix for the riscv toolchain in case it is not on the path")
set(RISCV_TOOLCHAIN_BASENAME "riscv32-unknown-elf" CACHE STRING "base name of the toolchain executables")


if("${RISCV_TOOLCHAIN_PREFIX}" STREQUAL "")
    set(RISCV_TOOLCHAIN "${RISCV_TOOLCHAIN_BASENAME}")
else()
    set(RISCV_TOOLCHAIN "${RISCV_TOOLCHAIN_PREFIX}/bin/${RISCV_TOOLCHAIN_BASENAME}")
endif()
if(WIN32)
    set(EXE_EXT ".exe")
endif()
set(CMAKE_C_COMPILER "${RISCV_TOOLCHAIN}-clang${EXE_EXT}")
set(CMAKE_CXX_COMPILER "${RISCV_TOOLCHAIN}-clang++${EXE_EXT}")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D__riscv__ -march=${RISCV_ARCH} -mabi=${RISCV_ABI} -fno-builtin-bcmp -Os ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D__riscv__ -march=${RISCV_ARCH} -mabi=${RISCV_ABI} -fno-builtin-bcmp -Os ")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -D__riscv__ -march=${RISCV_ARCH} -mabi=${RISCV_ABI} ")
set(CMAKE_EXE_LINKER_FLAGS "-march=${RISCV_ARCH} -mabi=${RISCV_ABI} -nostartfiles")
set(COMPILE_FLAGS "${COMPILE_FLAGS} -c")

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ${RISCV_ARCH})
