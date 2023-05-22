#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
	object03, // crc 
	object06 // insertsort
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object09, // matmult
		object03, // crc
		object14, // select
		object05, // fft
		object17, // statemate
		object13, // qurt
		object06, // insertsort
		object02, // bsort100
	} 
};


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
