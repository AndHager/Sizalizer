CC = ~/riscv_base/bin/clang

LLVM_MODULES = core jit native

CPPFLAGS = `llvm-config --cppflags`
LDFLAGS = `llvm-config --ldflags`
LIBS = `llvm-config --libs riscv riscvcodegen all`

all: main
	$(CC) -shared build/*.o $(LDFLAGS) $(LIBS) -o build/pass.so

main:
	$(CC) -c $(CPPFLAGS) -fpic src/pass.cpp -o build/pass.o