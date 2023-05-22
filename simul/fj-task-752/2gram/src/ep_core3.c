#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object09, // matmult
		object03, // crc
		object07, // jfdctint
		object17, // statemate
		object06, // insertsort
		object02, // bsort100
	}
};

/**
 * Entry point for core 3
 */
int
ep_core3(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}