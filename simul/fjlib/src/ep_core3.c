#include "ep.h"


extern object_t *fjnodes3[NUM_SECTIONS + 1];
extern object_t *pnodes3[NUM_SECTIONS][MAX_SEC_THREADS + 1];
/**
 * Entry point for core 3
 */
int
ep_core3(int hartid) {
	ep_dispatch(hartid, fjnodes3, pnodes3);
}
