#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
	object05, // fft 
	object16 // sqrt 
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object05, //fft
	object18, // ud
	object06, // insertsort
	object06, // insertsort
	object09, // matmult
	object16, // sqrt
	object15} // simple 
};


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
