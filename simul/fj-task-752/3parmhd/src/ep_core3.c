#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object07, // jfdctint
		object07, // jfdctint
		object07, // jfdctint
		object07, // jfdctint
		object07, // jfdctint
		object05, // fft
		object05, // fft
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object13, // qurt
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object01, // bs
		object01, // bs
		object02, // bsor100
		object02, // bsor100
	}
};

/**
 * Entry point for core 3
 */
int
ep_core3(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
