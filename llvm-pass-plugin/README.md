# LLVM Pass Plugin

Clang/LLVM supports dynamically loaded passes as plugins.
However, these plugins can't operate on the MIR, only on the
more abstract LLVM IR.

## Dependencies

- llvm
- g++
- clang (same version as llvm)

# Setup

Build memgraph container:

```bash
docker run -p 7687:7687 -p 7444:7444 -p 3000:3000 --name memgraph memgraph/memgraph-platform
```

Run memgraph:

```bash
docker start memgraph
```

Web interface available at: `http://localhost:3000/`

Memgraph graph style:

```json
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

Get whole Graph:

```json
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

Build pass with:

```bash
mkdir -p build
cd build
cmake ..
make
```

## Usage

```sh
$ clang -O3 -fpass-plugin=./build/libLLVMCDFG.so ...
```
