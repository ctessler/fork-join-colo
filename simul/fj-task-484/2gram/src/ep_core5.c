#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object13, // qurt
		object04, // expint
		object15, // simple
		object15, // simple
		object09, // matmult
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object18, // ud
		object16, // sqrt
		object16, // sqrt
		object11, // ns
		object02, // bsort100
		object17, // statemate
		object17, // statemate
	}
};

/**
 * Entry point for core 5
 */
int
ep_core5(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
