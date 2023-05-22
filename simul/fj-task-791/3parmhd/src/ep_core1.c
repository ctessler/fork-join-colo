#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
	object17, // statemate
	object14 // select
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
		object14, // select
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
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
		object17, // statemate
	}
};


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
