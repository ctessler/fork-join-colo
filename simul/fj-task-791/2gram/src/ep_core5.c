#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object14, // statemate
		object17, // select
		object17, // select
		object17, // select
		object17, // select
		object17, // select
		object17, // select
	}
};

/**
 * Entry point for core 5
 */
int
ep_core5(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}