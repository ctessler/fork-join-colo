#include "ep.h"


extern object_t *fjnodes5[NUM_SECTIONS + 1];
extern object_t *pnodes5[NUM_SECTIONS][MAX_SEC_THREADS + 1];
/**
 * Entry point for core 5
 */
int
ep_core5(int hartid) {
	ep_dispatch(hartid, fjnodes5, pnodes5);
}
