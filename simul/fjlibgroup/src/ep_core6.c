#include "ep.h"


extern object_t *fjnodes6[NUM_SECTIONS + 1];
extern object_t *pnodes6[NUM_SECTIONS][MAX_SEC_THREADS + 1];
/**
 * Entry point for core 6
 */
int
ep_core6(int hartid) {
	ep_dispatch(hartid, fjnodes6, pnodes6);
}
