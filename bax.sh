#!/bin/bash
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EMBENCH_DIR="${SCRIPT_ROOT}/embench-iot"

# Static analyze benchmark
${SCRIPT_ROOT}/static_analyze_embench_iot.sh

# Local build
${SCRIPT_ROOT}/local_build.sh

# Run benchmarks
cd "${EMBENCH_DIR}"
python3 ./benchmark_size.py --json-output --json-comma


cd ${SCRIPT_ROOT}