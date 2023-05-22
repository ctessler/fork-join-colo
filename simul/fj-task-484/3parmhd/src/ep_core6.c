#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object02, // bsort100
		object02, // bsort100
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
	}
};

/**
 * Entry point for core 6
 */
int
ep_core6(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}