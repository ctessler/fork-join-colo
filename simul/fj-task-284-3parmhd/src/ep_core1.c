#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
	object05, // fft
	object16 // sqrt
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
	object05, // fft
	object17, // statemate x 3
	object17,
	object17,
	object14, // select x 3 
	object14,
	object14,
	object18, // ud x 4 
	object18,
	object18,
	object18,
	object06, // insert sort x 5
	object06,
	object06,
	object06,
	object06,
	object11, // ns x 3 
	object11,
	object11,
	object10, // minver x 2 
	object10,
	object09, // matmult x 3
	object09,
	object09
	}
};


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
