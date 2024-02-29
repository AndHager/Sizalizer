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
set(ETISS_LDFLAGS "SHELL:-T${ETISS_LDSCRIPT} -lgloss -lsemihost")
message(CMAKE_EXE_LINKER_FLAGS=${CMAKE_EXE_LINKER_FLAGS})
set(ETISS_ELFINI ${CMAKE_CURRENT_SOURCE_DIR}/elffile.ini.in)
add_link_options("${ETISS_LDFLAGS}")
# NOTE: spec files do NOT work with clang (only gcc)
add_compile_options("--specs=./etiss-semihost.specs")


add_library(support support/beebsc.c support/main.c config/riscv32/chips/generic/chipsupport.c config/riscv32/boards/ri5cyverilator/boardsupport.c)
target_include_directories(support PUBLIC support)
target_compile_options(support PUBLIC -DWARMUP_HEAT=0)
add_subdirectory(riscv_crt0)
add_subdirectory(src)
