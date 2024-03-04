#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for file in aha-mont64 edn huffbench nettle-aes qrduino st matmult-int nettle-sha256 statemate crc32 minver nsichneu sglib-combined ud cubic nbody picojpeg slre wikisort;
do 
    echo "  INFO Executing: ${SCRIPT_ROOT}/../etiss/build/bin/bare_etiss_processor -pluginToLoad PrintInstruction -i${SCRIPT_ROOT}/embench-iot/bd/install/ini/${file}.ini"
    ${SCRIPT_ROOT}/../etiss/build/bin/bare_etiss_processor -pluginToLoad PrintInstruction -i${SCRIPT_ROOT}/embench-iot/bd/install/ini/${file}.ini &> ${SCRIPT_ROOT}/out/${file}_trace.txt
done
