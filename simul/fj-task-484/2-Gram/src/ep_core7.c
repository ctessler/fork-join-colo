#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object10, // minver
		object10, // minver
		object10, // minver
		object04, // expint
		object15, // simple
		object09, // matmult
		object09, // matmult
		object18, // ud
		object16, // sqrt
		object11, // ns
		object06, // insertsort
		object02, // bsort100
		object17, // statemate
	}
};

/**
 * Entry point for core 7
 */
int
ep_core7(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
