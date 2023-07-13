#include "ep.h"


extern object_t *fjnodes4[NUM_SECTIONS + 1];
extern object_t *pnodes4[NUM_SECTIONS][MAX_SEC_THREADS + 1];
/**
 * Entry point for core 4
 */
int
ep_core4(int hartid) {
	ep_dispatch(hartid, fjnodes4, pnodes4);
}
