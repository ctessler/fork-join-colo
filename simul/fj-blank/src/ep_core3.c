#include "ep.h"
#include "objects.h"

/**
 * Entry point for core 3
 */
int
ep_core3(int hartid) {
	object_t *fjnodes[NUM_SECTIONS + 1] = {
		NULL,
		NULL,
	};
	object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
		{NULL},
	};
	
	ep_dispatch(hartid, fjnodes, pnodes);
}
