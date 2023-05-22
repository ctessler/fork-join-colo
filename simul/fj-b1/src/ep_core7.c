#include "ep.h"
#include "objects.h"


/**
 * Entry point for core 7
 */
int
ep_core7(int hartid) {
	object_t *fjnodes[NUM_SECTIONS + 1] = {
	};
	object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	};
	ep_dispatch(hartid, fjnodes, pnodes);
}
