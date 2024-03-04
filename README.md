# Integrator

Integrates the static and the dynamic analysis in one Execution flow.

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
- time (explicitly installed not the bash func)
- python3
- pip3

### Python libs

- pathlib
- pyparsing
- numpy
- matplotlib
- neo4j

### Manually install

Graph DB and tools:

- memgraph graph db (https://memgraph.com/docs/getting-started)
- mgclient (https://github.com/memgraph/mgclient)
- mgconsole (https://github.com/memgraph/mgconsole)

Coss Compiler X86 -> RV32

- LLVM (https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2024.03.01/riscv32-elf-ubuntu-22.04-llvm-nightly-2024.03.01-nightly.tar.gz)

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


