#include "ep.h"


extern object_t *fjnodes2[NUM_SECTIONS + 1];
extern object_t *pnodes2[NUM_SECTIONS][MAX_SEC_THREADS + 1];
/**
 * Entry point for core 2
 */
int
ep_core2(int hartid) {
	ep_dispatch(hartid, fjnodes2, pnodes2);
}
