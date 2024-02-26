FROM ubuntu:22.04
LABEL version="1.0"
LABEL description="Integrator"
# apt prompts
RUN apt-get update
RUN apt-get upgrade -y
# install deps
RUN apt-get install -y fish \
                    binutils \
                    grep \
                    sed \
                    build-essential \
                    make \
                    cmake \
                    clang \
                    llvm \
                    pkg-config \
                    python3 \
                    python3-pip \
                    python-is-python3 \
                    git \
                    zip \
                    gzip \
                    unzip \
                    wget \
                    dbus \
                    ninja-build \
                    meson \
                    m4 \
                    gperf \
                    gcc \
                    g++ \
                    nano \
                    strace \
                    cproto \
                    autoconf \
                    automake \
                    curl \
                    gawk \
                    bison \
                    flex \
                    texinfo \
                    gperf \
                    libtool \
                    patchutils \
                    bc \
                    libssl-dev \
                    libmount-dev \
                    libfdt-dev \
                    libseccomp-dev \
                    autotools-dev \
                    libexpat1-dev \
                    libpixman-1-dev \
                    libmpc-dev \
                    libmpfr-dev \
                    libgmp-dev \
                    libcap-dev \
                    zlib1g-dev \
                    libexpat-dev \
                    libglib2.0-dev


RUN pip3 install pyelftools

#####################################
#### Copy folders of the context ####
#####################################
WORKDIR /
    COPY static_analyze_embench_iot.sh /
    COPY embench-iot /embench-iot

    COPY seal /seal

##################################
#### Download riscv Toolchain ####
##################################
WORKDIR /opt
    RUN wget https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2023.11.22/riscv32-glibc-ubuntu-22.04-llvm-nightly-2023.11.22-nightly.tar.gz
    RUN tar xf riscv32-glibc-ubuntu-22.04-llvm-nightly-2023.11.22-nightly.tar.gz
    RUN rm riscv32-glibc-ubuntu-22.04-llvm-nightly-2023.11.22-nightly.tar.gz

###########################################
#### Build Clang, Passes and set paths ####
###########################################
WORKDIR /
    RUN wget https://github.com/memgraph/mgclient/archive/refs/tags/v1.4.2.zip
    RUN unzip v1.4.2.zip
    RUN rm v1.4.2.zip

WORKDIR /mgclient-1.4.2
    RUN mkdir -p build

WORKDIR /mgclient-1.4.2/build
    RUN cmake ..
    RUN make
    RUN make install


WORKDIR /seal/llvm-pass-plugin
    RUN mkdir -p build

WORKDIR /seal/llvm-pass-plugin/build
    RUN cmake ..
    RUN make

WORKDIR /
#    RUN ./static_analyze_embench_iot.sh --clean

# WORKDIR /llvm-project
    # Set Path to compilde clang, clang++, ...
#     ARG BUILD_PATH="/llvm-project/build"
#     ARG BUILD_BIN="$BUILD_PATH/bin"
#     ARG BUILD_LIB="$BUILD_PATH/lib"

#     ARG CLANGPP="$BUILD_BIN/clang++"
#     ARG CLANG="$BUILD_BIN/clang"

#     ARG LOAD_FLAGS="-Xclang -load -Xclang"

WORKDIR /
#    RUN export ASAN_SYMBOLIZER=$BUILD_BIN/llvm-symbolizer
#     RUN export ASAN_OPTIONS=detect_leaks=0

