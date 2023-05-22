#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object09, // matmult
		object09, // matmult
		object09, // matmult
		object09, // matmult
		object09, // matmult
		object09, // matmult
		object09, // matmult
	}
};

/**
 * Entry point for core 7
 */
int
ep_core7(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}