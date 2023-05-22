#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object11, // ns
		object11, // ns
		object15, // simple
		object15, // simple
		object18, // ud
		object18, // ud
		object10, // minver
		object04, // expint
		object14, // select
		object07, // jfdctint
		object17, // statemate
		object01, //
	}
};

/**
 * Entry point for core 6
 */
int
ep_core6(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
