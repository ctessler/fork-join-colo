#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object11, // ns
		object11, // ns
		object15, // simple
		object18, // ud
		object18, // ud		
		object08, // lcdnum
		object10, // minver
		object04, // expint
		object14, // select
		object07, // jfdctint
		object13, // qurt
		object13, // qurt
		object01, // bs
	}
};

/**
 * Entry point for core 7
 */
int
ep_core7(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
