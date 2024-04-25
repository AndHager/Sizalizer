#!/bin/bash
# Author: Andreas Hager-Clukas
# Email: andreas.hager-clukas@hm.edu
set -ue

SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_TARGET=${SCRIPT_ROOT}/target_scrips
OUT_DIR=${SCRIPT_ROOT}/out

# Set default values
clean=false

musl=false
embench=false

start_db=false
purge_db=false
build_dfg=false
analyze_dfg=false
build_target=false
analyze_binary=false
run_embench_size=false
run_etiss_embench=false
analyze_traces=false

debug=false

# Usage manual entry
usage() {
    cat << EOF
Usage: ${0##*/} [OPTIONS]

This script builds and executes the Analysis for Embench-iot.

Available options:

    --clean               Clean run full analysis (default: $clean)
    --musl                Set target to musl (default: $musl)
    --embench             set target to Embench (dfault: $embench)
    --start-db            Start the database service (default: $start_db)
    --purge-db            Purge the database (default: $purge_db)
    --build-dfg           Build the data flow graph (default: $build_dfg)
    --analyze-dfg         Analyze the data flow graph (default: $analyze_dfg)
    --build-target        Build target (default: $build_target)
    --analyze-binary      Analyze binary files (default: $analyze_binary)
    --run-embench-size    Run Embench benchmark for size (default: $run_embench_size)
    --run-etiss-embench   Run ETISS with Embench benchmark (default: $run_etiss_embench)
    --analyze-traces      Enable trace analysis (default: $analyze_traces)
    --help                Display this help and exit

EOF
    exit
}


# Loop through arguments and process them
for arg in "$@"
do
  case $arg in
    --clean)
    clean=true
    shift # Remove --clean from processing
    ;;
    --start-db)
    start_db=true
    shift # Remove --start-db from processing
    ;;
    --embench)
    embench=true
    shift # Remove --embench from processing
    ;;
    --musl)
    musl=true
    shift # Remove --musl from processing
    ;;
    --purge-db)
    purge_db=true
    shift # Remove --purge-db from processing
    ;;
    --build-dfg)
    build_dfg=true
    shift # Remove --build-dfg from processing
    ;;
    --analyze-dfg)
    analyze_dfg=true
    shift # Remove --analyze-dfg from processing
    ;;
    --build-target)
    build_target=true
    shift # Remove --build-embench from processing
    ;;
    --analyze-binary)
    analyze_binary=true
    shift # Remove --analyze-binary from processing
    ;;
    --run-embench-size)
    run_embench_size=true
    shift # Remove --run-embench-size from processing
    ;;
    --run-etiss-embench)
    run_etiss_embench=true
    shift # Remove --run-etiss-embench from processing
    ;;
    --analyze-traces)
    analyze_traces=true
    shift # Remove --analyze-traces from processing
    ;;
    --help)
    usage
    ;;
    *)
    # Unknown option
    echo "Error: Invalid option $arg"
    exit 1
    ;;  
  esac
done

if [ "$clean" = true ] ; then
    start_db=true
    purge_db=true
    build_llvm=true
    build_dfg=true
    analyze_dfg=true
    build_target=true
    analyze_binary=true

    run_embench_size=true
    run_etiss_embench=true

    analyze_traces=true
fi

if [ "$debug" = true ] ; then
    echo "INFO params:"
    echo "  clean=$clean"
    echo "  start_db=$start_db"
    echo "  purge_db=$purge_db"
    echo "  build_llvm=$build_llvm"
    echo "  build_dfg=$build_dfg"
    echo "  analyze_dfg=$analyze_dfg"
    echo "  build_target=$build_target"
    echo "  analyze_binary=$analyze_binary"

    if [ "$embench" = true ] ; then
        echo "  run_embench_size=$run_embench_size"
        echo "  run_etiss_embench=$run_etiss_embench"
    fi 

    echo "  analyze_traces=$analyze_traces"
fi


if [ "$clean" = true ] ; then
    echo "INFO: Cleaning old out"
    rm -r ${OUT_DIR}
    mkdir out
fi

if [ "$purge_db" = true ] ; then
    echo "INFO: Start memgraph"
    docker start memgraph &> ${OUT_DIR}/docker_start_out.txt
fi

if [ "$purge_db" = true ] ; then
    echo "INFO: Purge db"
    echo "MATCH (N) DETACH DELETE N;" | mgconsole
fi

if [ "$build_dfg" = true ] ; then
    # build dfg pass
    echo "INFO: Build DFG analysis LLVM-Pass"
    ${SCRIPT_ROOT}/build_dfg_pass.sh &> ${OUT_DIR}/dfg_pass_build.txt

    # Static analyze benchmark
    echo "INFO: Building DFG"
    if [ "$embench" = true ] ; then
        ${SCRIPT_ROOT}/static_dfg_analyze_embench_iot.sh &> ${OUT_DIR}/embench_dfg_pass_run.txt
    fi 

    if [ "$musl" = true ] ; then
        ${SCRIPT_ROOT}/static_dfg_analyze_musl.sh &> ${OUT_DIR}/musl_dfg_pass_run.txt
    fi 
fi

if [ "$analyze_dfg" = true ] ; then
    echo "INFO: Analyzing DFG"
    python3 ${SCRIPT_ROOT}/seal/analysis/static/main.py --pdc True &> ${OUT_DIR}/dfg_analysis.txt
fi

if [ "$build_target" = true ] ; then
    if [ "$embench" = true ] ; then
        echo "INFO: Building embench"
        ${SCRIPT_ROOT}/compile_embench_iot.sh &> ${OUT_DIR}/embench_build.txt

        echo "INFO: Building embench for ETISS"
        ${SCRIPT_ROOT}/build_for_etiss.sh  &> ${OUT_DIR}/embench_for_etiss_build.txt
    fi 

    if [ "$musl" = true ] ; then
        echo "INFO: Building musl"
        ${SCRIPT_ROOT}/compile_musl.sh &> ${OUT_DIR}/musl_build.txt


        echo "INFO: Building bench for musl"
        echo "TODO: select bench" # maybe https://www.stupid-projects.com/posts/compile-benchmarks-with-gcc-musl-and-clang/ https://bitbucket.org/dimtass/gcc_musl_clang_benchmark/src/master/
    fi 
fi

if [ "$analyze_binary" = true ] ; then
    if [ "$embench" = true ] ; then
        echo "INFO: Disassembling Binaries"
        ${SCRIPT_ROOT}/disassemble_embench_bins.sh

        echo "INFO: Static analyzing the binaries of Embench-iot"
        ${SCRIPT_ROOT}/static_analyze_embench.sh
    fi 

    if [ "$musl" = true ] ; then
        echo "INFO: Disassembling Binaries"
        ${SCRIPT_ROOT}/disassemble_musl_bins.sh

        echo "INFO: Static analyzing the binaries of musl"
        ${SCRIPT_ROOT}/static_analyze_musl.sh
    fi 
fi

if [ "$run_embench_size" = true ] ; then
    echo "INFO: Executing the static size benchmark of Embench-iot"
    python3  ${SCRIPT_ROOT}/embench-iot/benchmark_size.py --json-output --json-comma &> ${OUT_DIR}/embench_static_size.json
fi

if [ "$run_etiss_embench" = true ] ; then
    echo "INFO: Generating the dynamic traces for Embench-iot"
    ${SCRIPT_ROOT}/execute_etiss_embench.sh
fi

if [ "$analyze_traces" = true ] ; then
    echo "INFO: Analyzing traces"
    cd ${OUT_DIR} 
    TRACES=$(printf  '%s ' *_trace.txt)
    cd ${SCRIPT_ROOT}
    # echo "  INFO Executing: python3 ${SCRIPT_ROOT}/seal/analysis/dynamic/main.py --path ${OUT_DIR} ${TRACES}"
    python3 ${SCRIPT_ROOT}/seal/analysis/dynamic/main.py --path ${OUT_DIR} ${TRACES}
fi

cd ${SCRIPT_ROOT}
