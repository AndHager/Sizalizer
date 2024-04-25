#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MASK 0xFFFFFFFF

void init();
unsigned int __attribute__ ((noinline)) nand(unsigned int i, unsigned int j);

int main()
{
    init();
    unsigned int i = MASK - rand() % 100;
    unsigned int na = nand(i, MASK);
    printf("0x%x NAND 0x%x == 0x%x\n", i, MASK, na);
    return EXIT_SUCCESS;
}

void init() {
    srand(time(NULL));
}

unsigned int __attribute__ ((noinline)) nand(unsigned int i, unsigned int j) {
    return ~(i & j);
}
