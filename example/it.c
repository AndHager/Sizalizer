#include <stdio.h>
#include <stdlib.h>

int main() {

  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < i; j++) {
      int m = i^j;
      printf("%x XOR %3x == %3x\n", i, j, m);
    }
  }

  return EXIT_SUCCESS;
}
