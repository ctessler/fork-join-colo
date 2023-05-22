#include "ep.h"

void
ep_dispatch(int hartid, object_t **fjnodes,
	    object_t *pnodes[][MAX_SEC_THREADS + 1]) {
	for (int sec=0; sec < NUM_SECTIONS; sec++) {
		/* fork-join node */
		EC_READY(hartid);
		if (fjnodes[sec]) {
			fjnodes[sec]();
		}
		EC_DONE(hartid);

		/* Threads */
		EC_READY(hartid);
		for (int t=0; pnodes[sec][t] != NULL; t++) {
			pnodes[sec][t]();
		}
		EC_DONE(hartid);
	}

	/* terminal fork-join node */
	EC_READY(hartid);
	if (fjnodes[NUM_SECTIONS]) {
		fjnodes[NUM_SECTIONS]();
	}
	EC_DONE(hartid);
	

	/* Ready to shut down */
	EC_READY(hartid);
	/*
	 * Should never reach here
	 *
	 * Reaching this instruction likely means NUM_SECTIONS is set
	 * incorrectly. 
	 */
	asm("ebreak"); 
}


int
ep_ph1(int hartid) {
	/* source fork-join node */
	EC_READY(hartid);
	/* fork-join code */
	EC_DONE(hartid);

	/* parallel section */
	EC_READY(hartid);
	/* threads */
	EC_DONE(hartid);

	/* terminal fork-join node */
	EC_READY(hartid);
	/* fork-join code */
	EC_DONE(hartid);

	
	/* Wait to terminate */
	EC_READY(hartid);
	/*
	 * Should never reach here
	 *
	 * Reaching this instruction likely means NUM_SECTIONS is set
	 * incorrectly. 
	 */
	asm("ebreak"); 
}

int
ep_ph2(int hartid) {
	/* source fork-join node */
	EC_READY(hartid);
	/* fork-join code */
	EC_DONE(hartid);

	/* parallel section */
	EC_READY(hartid);
	/* threads */
	EC_DONE(hartid);

	/* intermediate fork-join node */
	EC_READY(hartid);
	/* fork-join code */
	EC_DONE(hartid);
	
	/* parallel section */
	EC_READY(hartid);
	/* threads */
	EC_DONE(hartid);

	/* terminal fork-join node */
	EC_READY(hartid);
	/* fork-join code */
	EC_DONE(hartid);

	
	/* Wait to terminate */
	EC_READY(hartid);
	/*
	 * Should never reach here
	 *
	 * Reaching this instruction likely means NUM_SECTIONS is set
	 * incorrectly. 
	 */
	asm("ebreak"); 
}
