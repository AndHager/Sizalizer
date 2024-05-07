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


## Setup

Build memgraph container:

```bash
docker run -p 7687:7687 -p 7444:7444 -p 3000:3000 --name memgraph memgraph/memgraph-platform
```

Build LLVM CDFG pass with:

```bash
cd llvm-pass-plugin
mkdir -p build
cd build
cmake ..
make
cd ../..
```

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


### Memgraph

Used to store the CDFG

#### Start memgraph seperatly

```bash
docker start memgraph
```

Web interface available at: `http://localhost:3000/`

##### Standard graph style

Memgraph graph style:

```
@NodeStyle {
  size: 3
  label: Property(node, "name")
  border-width: 1
  border-color: #ffffff
  shadow-color: #333333
  shadow-size: 20
}

@EdgeStyle {
  width: 0.4
  label: Type(edge)
  arrow-size: 1
  color: #6AA84F
}
```

##### Some Queries

Get whole Graph:

```
MATCH p=(n)-[r]-(m)
RETURN *;
```

Get chains of equal instructions (excluding const):

```
MATCH (n)
MATCH (m)
WHERE (NOT n.name = 'Const') AND (NOT m.name = 'Const') AND n.name = m.name
MATCH p=(n)-[r:DFG]-(m)
RETURN *;
```

Get matching pairs of instructions:

```
MATCH (n1) 
MATCH (m1)
MATCH (n2)
MATCH (m2)
MATCH p1=(n1)-[r1:DFG]->(m1)
MATCH p2=(n2)-[r2:DFG]->(m2)
WHERE (NOT n1.name = 'Const') AND (NOT m1.name = 'Const') AND n1.name = n2.name AND m1.name = m2.name AND n1 != n2 AND m1 != m2
RETURN *;
```

Get matching triples of instructions:

```
MATCH p1=(n1)-[r1:DFG]->(m1)-[i1:DFG]->(j1)
MATCH p2=(n2)-[r2:DFG]->(m2)-[i2:DFG]->(j2)
WHERE ((NOT n1.name = 'Const') AND (NOT m1.name = 'Const') AND (NOT j1.name = 'Const')
    AND (NOT n1.name = 'phi') AND (NOT m1.name = 'phi') AND (NOT j1.name = 'phi')
    AND (NOT n1.name = 'call') AND (NOT m1.name = 'call') AND (NOT j1.name = 'call')
    AND n1.name = n2.name AND m1.name = m2.name AND j1.name = j2.name 
    AND n1 != n2 AND m1 != m2 AND j1 != j2)
RETURN p1;
```

Get load -> X -> store triplet:
```
MATCH p=(n0)-[:DFG]->(n1)-[:DFG]->(n2)
WHERE (
  NOT n0.name = 'Const' 
  AND NOT n1.name = 'Const' 
  AND NOT n2.name = 'Const'
  AND n0.name = 'load'
  AND n2.name = 'store'
)
RETURN p;
```


### Usage of LLVM CDFG generation Pass

```sh
$ clang -O3 -fpass-plugin=./build/libLLVMCDFG.so ...
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

