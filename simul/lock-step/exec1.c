#include "csched.h"
#include "lockstep.h"

#define REPIT 1000000

int exec1(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;
}

int exec2(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;
}

int exec3(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;	
}

int exec4(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;	
}

int exec5(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;	
}

int exec6(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;	
}

int exec7(int hartid) {
	EC_READY(hartid);
	EC_START(hartid);
	for (int i=0; i<(hartid * REPIT); i++) {
	}

	/* done with the last section */
	EC_READY(hartid);	
	return 0;	
}
