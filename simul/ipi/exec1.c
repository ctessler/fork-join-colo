#include "csched.h"
#include "lockstep.h"

#define REPIT 1000

int exec1(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);

	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);
	return 0;
}
