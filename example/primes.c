#include <stdio.h>
#include <stdbool.h>

int check_prime(int);

int main() {

  int n1 = 2;
  int n2 = 100;
  bool flag;

  // swapping n1 and n2 if n1 is greater than n2
  if (n1 > n2) {
    n2 = n1 + n2;
    n1 = n2 - n1;
    n2 = n2 - n1;
  }

  printf("Prime numbers between %d and %d are:\n", n1, n2);

  for(int i = n1; i < n2; ++i) {
    // if i is a prime number, flag will be equal to 1
    flag = check_prime(i);

    if(flag)
      printf("%d, ", i);
  }
  puts("");
  return 0;
}

// user-defined function to check prime number
int check_prime(int n) {
  bool is_prime = true;

  // 0 and 1 are not prime numbers
  if (n == 0 || n == 1) {
    is_prime = false;
  }
  
  for(int j = 2; j <= n/2; ++j) {
    if (n%j == 0) {
      is_prime = false;
      break;
    }
  }

  return is_prime;
}