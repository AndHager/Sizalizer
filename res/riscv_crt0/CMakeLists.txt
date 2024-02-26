cmake_minimum_required(VERSION 3.10)

project(riscv_crt0 C CXX ASM)

add_library(etiss_crt0 STATIC crt0.S fixes.c trap_handler.c)
