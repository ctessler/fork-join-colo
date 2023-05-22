#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object09, // matmult
		object03, // crc
		object14, // select
		object05, // fft
		object17, // statemate
		object06, // insertsort
		object06, // insertsort		
	}
};

/**
 * Entry point for core 2
 */
int
ep_core2(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
