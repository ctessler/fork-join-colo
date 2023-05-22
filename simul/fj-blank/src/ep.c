#include "ep.h"

void
ep_dispatch(int hartid, object_t **fjnodes,
	    object_t *pnodes[][MAX_SEC_THREADS + 1]) {
	for (int sec=0; sec < NUM_SECTIONS; sec++) {
		/* fork-join node */
		EC_READY(hartid);
		EC_WAIT_START(hartid);
		if (fjnodes[sec]) {
			fjnodes[sec]();
		}
		EC_DONE(hartid);

		/* Threads */
		EC_READY(hartid);
		EC_WAIT_START(hartid);
		for (int t=0; pnodes[sec][t] != NULL; t++) {
			pnodes[sec][t]();
		}
		EC_DONE(hartid);
	}

	/* terminal fork-join node */
	EC_READY(hartid);
	EC_WAIT_START(hartid);
	if (fjnodes[NUM_SECTIONS]) {
		fjnodes[NUM_SECTIONS]();
	}
	EC_DONE(hartid);
	
	/* Ready to shut down */
	EC_READY(hartid);
	WFI;
}
	
