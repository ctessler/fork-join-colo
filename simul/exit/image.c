void exit(void) {
	unsigned int *DMA_EXIT = (unsigned int *) 0x100000;
	*DMA_EXIT = 0x3333;
}

int
main(int argc, char** argv) {
	/* The following **ONLY** works if hartid is a register */
	int *hartid;
	asm volatile( "add %0, gp, zero"
		      : "=r" (hartid));
	/* The problem to solve is storing the gp pointer onto a stack variable */

	if (*hartid != 0) {
		asm volatile("wfi");
	}
	
	exit();
};

