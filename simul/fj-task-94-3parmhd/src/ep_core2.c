#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object07}
};

/**
 * Entry point for core 2
 */
int
ep_core2(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
