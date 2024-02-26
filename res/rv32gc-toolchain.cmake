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

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D__riscv__ -march=${RISCV_ARCH} -mabi=${RISCV_ABI} -fno-builtin-bcmp -Oz -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/support -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/boards/ri5cyverilator -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/chips/generic -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32 -DCPU_MHZ=1 -DWARMUP_HEAT=1")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D__riscv__ -march=${RISCV_ARCH} -mabi=${RISCV_ABI} -fno-builtin-bcmp -Oz -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/support -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/boards/ri5cyverilator -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/chips/generic -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32 -DCPU_MHZ=1 -DWARMUP_HEAT=1")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -D__riscv__ -march=${RISCV_ARCH} -mabi=${RISCV_ABI}")
set(CMAKE_EXE_LINKER_FLAGS "-march=${RISCV_ARCH} -mabi=${RISCV_ABI} -nostartfiles -nostdlib /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/config/riscv32/chips/generic/chipsupport_etiss.o /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/config/riscv32/boards/ri5cyverilator/boardsupport_etiss.o /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/main_etiss.o /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/beebsc_etiss.o /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-crt0_etiss.o    /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-libc_etiss.o /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-libgcc_etiss.o /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-libm_etiss.o")

## Build
#/opt/riscv-elf/bin/clang 
#   -fno-builtin-bcmp 
#   -Oz 
#   -msave-restore 
#   -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/support 
#   -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/boards/ri5cyverilator 
#   -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/chips/generic 
#   -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32 
#   -DCPU_MHZ=1 
#   -DWARMUP_HEAT=1 
#   -o libud.o 
#   -c /home/ahc/Desktop/CodeComp/integrator/embench-iot/src/ud/libud.c

## Link
#/opt/riscv/bin/clang 
#   -nostartfiles -nostdlib 
#   -o wikisort libwikisort.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/config/riscv32/chips/generic/chipsupport.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/config/riscv32/boards/ri5cyverilator/boardsupport.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/main.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/beebsc.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-crt0.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-libc.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-libgcc.o 
#   /home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/support/dummy-libm.o


set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ${RISCV_ARCH})
