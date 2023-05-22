#include "csched.h"
#include "lockstep.h"


/* Global variables needed for the lock-step protocol */
unsigned int __LS_SIGNAL=0;
unsigned int __LS_READY[NUM_CORES];
unsigned int __LS_STARTED[NUM_CORES];

/**
 * Controlling core code
 */
int control(int);

/* The entry points for each of the core schedules */
csched_t* scheds[NUM_CORES] = {
	control,
	exec1,
	exec1,
	exec1,
	exec1,
	exec1,
	exec1,
	exec1,
};


int
main(int argc, char** argv) {
	/* The following **ONLY** works if hartid is a register */
	int *hartid;
	asm volatile( "add %0, gp, zero"
		      : "=r" (hartid));
	/* The problem to solve is storing the gp pointer onto a stack variable */

	scheds[*hartid](*hartid);
	while (1) {
		CLEAR_PENDING_INTS(*hartid);
		asm("wfi");
	}
};

int
control(int hartid) {
	__LS_SIGNAL = 0;
	CC_SIGNAL();
	CC_RESET();

	CC_SIGNAL();
	return 0;
}
