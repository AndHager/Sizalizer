#!/bin/bash
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EMBENCH_DIR="${SCRIPT_ROOT}/embench-iot"

# Start and clear DB
docker start memgraph
echo "MATCH (N) DETACH DELETE N;" | mgconsole

# Static analyze benchmark
${SCRIPT_ROOT}/static_analyze_embench_iot.sh

# Local build
${SCRIPT_ROOT}/local_build.sh
${SCRIPT_ROOT}/build_for_etiss.sh

# Run benchmarks
cd "${EMBENCH_DIR}"
python3 ./benchmark_size.py --json-output --json-comma &> ${SCRIPT_ROOT}/out/embench_static_size.json


for file in aha-mont64 edn huffbench nettle-aes qrduino st matmult-in nettle-sha256 statemate crc32 minver nsichneu sglib-combine ud cubic nbod picojpeg slre wikisort;
do 
    ${SCRIPT_ROOT}/../etiss/build/bin/bare_etiss_processor -pluginToLoad PrintInstruction -i/home/ahc/Desktop/CodeComp/integrator/embench-iot/bd/install/ini/${file}.ini &> ${SCRIPT_ROOT}/out/${file}_trace.txt
done


cd ${SCRIPT_ROOT}