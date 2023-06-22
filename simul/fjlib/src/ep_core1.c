#include "ep.h"


extern object_t *fjnodes1[NUM_SECTIONS + 1];
extern object_t *pnodes1[NUM_SECTIONS][MAX_SEC_THREADS + 1];


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes1, pnodes1);
}
