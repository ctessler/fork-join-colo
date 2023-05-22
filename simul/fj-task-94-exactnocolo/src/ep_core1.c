#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
	object06,
	object06
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object08}
};


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
