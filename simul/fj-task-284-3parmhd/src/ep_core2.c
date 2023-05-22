#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
	object09, // matmult x 2 
	object09,
	object02, // bsort100 x2 
	object02,
	object07, // jfdctint x7
	object07,
	object07,
	object07,
	object08, // lcdnum
	object16, // sqrt x2 
	object16,
	object03, // crc 
	object13, // qurt x 2
	object13, 
	}
};

/**
 * Entry point for core 2
 */
int
ep_core2(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
