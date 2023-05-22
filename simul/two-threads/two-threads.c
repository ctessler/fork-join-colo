/**
 * We need "core-local" storage
 *
 * 
 */
int hartid;

/*
 * Reads a CSR into value, csrid must be a compile time integer
 * in the range 0-4096
 */
#define CSR_READ(value, csrid)			\
	asm volatile("csrr %0, %1"		\
       /* output */  : "=r" (value)		\
       /* input */   : "n" (csrid)		\
		     : /* clobbers none */);

int path_core_one(int x);
int path_core_two(int y);

int main() {
  int a = 4;
  int b = 12;

  /* The following **ONLY** works if hartid is a register */
  int *hartid;
  asm volatile( "add %0, gp, zero"
		: "=r" (hartid));
  /* The problem to solve is storing the gp pointer onto a stack variable */

  if (*hartid == 1) {
    path_core_one(27);
  }
  if (*hartid == 0) {
    path_core_two(42);
  }

  /** Unreachable ... supposedly */
  asm volatile ("ebreak");
  return 0;
}

int path_core_one(int x) {
  while (1) {
    int z = x + 2;
  }
  return 1;
};


int path_core_two(int x) {
  while (1) {
    int z = x + 2;
  }
  return 1;
};
