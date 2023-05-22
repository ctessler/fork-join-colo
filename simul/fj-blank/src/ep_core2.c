#include "ep.h"
#include "objects.h"


/**
 * Entry point for core 2
 */
int
ep_core2(int hartid) {
	object_t *fjnodes[NUM_SECTIONS + 1] = {
		NULL,
		NULL,
	};
	object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
		{NULL},
	};

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
