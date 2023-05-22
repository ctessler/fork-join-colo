#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object14, // select
	object18, // ud 
	object06, // insertsort
	object11, // ns
	object02, // bssort100
	object07, // jfdctint
	object13, // qurt
	object12 // nsichneu
	}
};

/**
 * Entry point for core 6
 */
int
ep_core6(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
