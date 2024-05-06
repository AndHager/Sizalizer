# Sizalizer: A Multi-layer Analysis Framework for ISA Optimization

Sizalizer is an innovative analysis framework designed to advance the development of embedded C/C++ applications alongside RISC-V instruction set extensions. 


## Prerequisites

It is tested on Ubuntu 22.04


### Tools

- git 
- cmake 
- make 
- gcc 
- g++ 
- docker
- binwalk
- readelf
- objdump
- time (explicitly installed not the bash func)
- python3
- pip3


### Python libs

- pathlib
- pyparsing
- numpy
- matplotlib
- neo4j
- enum


### Manually install

Graph DB and tools:

- memgraph graph db (https://memgraph.com/docs/getting-started)
- mgclient (https://github.com/memgraph/mgclient)
- mgconsole (https://github.com/memgraph/mgconsole)

Coss Compiler X86 -> RV32

- Prebuild RISC-V toolchain (https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2024.03.01/riscv32-elf-ubuntu-22.04-llvm-nightly-2024.03.01-nightly.tar.gz)
- Manually build clang version 18.1.3: (https://github.com/llvm/llvm-project/releases/tag/llvmorg-18.1.3)


## Usage

Use the `bax.sh` script in order to execute the analysis process.

```bash
Usage: bax.sh [OPTIONS]

This script builds and executes the Analysis for Embench-iot.

Available options:

    --clean               Enable cleaning operation (default: true)
    --start-db            Start the database service (default: false)
    --purge-db            Purge the database (default: false)
    --build-dfg           Build the data flow graph (default: false)
    --analyze-dfg         Analyze the data flow graph (default: false)
    --build-embench       Build Embench benchmark (default: false)
    --analyze-binary      Analyze binary files (default: false)
    --run-embench-size    Run Embench benchmark for size (default: false)
    --run-etiss-embench   Run ETISS with Embench benchmark (default: false)
    --analyze-traces      Enable trace analysis (default: true)
    --help                Display this help and exit
```


### DFG Analysis

The DFG analysis can be conducted separately:

```
usage: analysis/dfg.py [-h] [--host [HOST]] [--port [PORT]] [--pdc [PDC]] [--clear-db [CLEAR_DB]]

Analyze the File.

options:
  -h, --help            show this help message and exit
  --host [HOST]         host of the memgraph (or Neo4j) DB (reachable over bolt)
  --port [PORT]         port of the Memgraph DB
  --pdc [PDC]           Plot Duplicated Chains
  --clear-db [CLEAR_DB] Clear the Database
```


### Binary Analysis

You may want to use the binary analysis script separately:

```
usage: analysis/static.py [-h] [--path PATH] F [F ...]

Count the instructions in an assembly file.

positional arguments:
  F            files to analyze

options:
  -h, --help   show this help message and exit
  --path PATH  base path for the files
```


### Trace Analysis

The DFG analysis can be conducted separately:

```
usage: analysis/dynamic.py [-h] [--path PATH] F [F ...]

Count the instructions in an trace file.

positional arguments:
  F            files to analyze

options:
  -h, --help   show this help message and exit
  --path PATH  base path for the files
```

