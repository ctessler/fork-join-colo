#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object09, // matmult
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object16, // sqrt
		object11, // ns
		object11, // ns
		object11, // ns
		object11, // ns
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object06, // insertsort
		object02, // bsort100
	}
};

/**
 * Entry point for core 4
 */
int
ep_core4(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
