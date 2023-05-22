#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object07, object06, object06}
};

/**
 * Entry point for core 4
 */
int
ep_core4(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
