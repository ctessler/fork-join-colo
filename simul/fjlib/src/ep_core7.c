#include "ep.h"


extern object_t *fjnodes7[NUM_SECTIONS + 1];
extern object_t *pnodes7[NUM_SECTIONS][MAX_SEC_THREADS + 1];
/**
 * Entry point for core 7
 */
int
ep_core7(int hartid) {
	ep_dispatch(hartid, fjnodes7, pnodes7);
}
