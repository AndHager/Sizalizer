cmake_minimum_required(VERSION 3.10)

set(CMAKE_TRY_COMPILE_TARGET_TYPE "STATIC_LIBRARY")
project(embench_for_etiss)

set(MEM_ROM_ORIGIN 0x10000000)
set(MEM_ROM_LENGTH 0x00400000)
set(MEM_RAM_ORIGIN 0x20000000)
set(MEM_RAM_LENGTH 0x00100000)

set(MIN_STACK_SIZE 0x1000)
set(MIN_HEAP_SIZE 0x1000)

configure_file(etiss.ld.in etiss.ld @ONLY)
configure_file(memsegs.ini.in memsegs.ini @ONLY)

set(ETISS_LDSCRIPT ${CMAKE_CURRENT_BINARY_DIR}/etiss.ld)
set(ETISS_LDFLAGS "-L${CMAKE_CURRENT_BINARY_DIR}/riscv_crt0 --specs=${CMAKE_CURRENT_SOURCE_DIR}/etiss-semihost.specs -T ${ETISS_LDSCRIPT}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${ETISS_LDFLAGS}")
message(CMAKE_EXE_LINKER_FLAGS=${CMAKE_EXE_LINKER_FLAGS})
set(ETISS_ELFINI ${CMAKE_CURRENT_SOURCE_DIR}/elffile.ini.in)


#clang -fno-builtin-bcmp -Oz -fpass-plugin=/home/ahc/Desktop/CodeComp/integrator/seal/llvm-pass-plugin/build/libLLVMCDFG.so -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/support -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/boards/ri5cyverilator -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32/chips/generic -I/home/ahc/Desktop/CodeComp/integrator/embench-iot/config/riscv32 -DCPU_MHZ=1 -DWARMUP_HEAT=1 -o beebsc.o -c /home/ahc/Desktop/CodeComp/integrator/embench-iot/support/beebsc.c

add_subdirectory(riscv_crt0)
add_subdirectory(src)

