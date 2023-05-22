#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
	object01, // bs
	object15  // simple
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select

		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt

		object10, // minver
		object10, // minver
		object10, // minver
		object10, // minver
		object10, // minver
		object10, // minver
		object10, // minver
		object10, // minver

		object04, // expint
		object04, // expint
		object04, // expint
		object04, // expint
		object04, // expint
		object04, // expint
		object04, // expint
		object04, // expint
		object04, // expint

		object15, // simple
		object15, // simple
		object15, // simple
		object15, // simple
		object15, // simple
		object15, // simple
		object15, // simple
		object15, // simple

		object09, // matmult
		object09, // matmult
	}
};


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
