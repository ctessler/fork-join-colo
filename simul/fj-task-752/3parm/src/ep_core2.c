#include "ep.h"
#include "objects.h"

static object_t *fjnodes[NUM_SECTIONS + 1] = {
};
static object_t *pnodes[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object09, // matmult
		object11, // ns
		object11, // ns
		object11, // ns
		object11, // ns
		object15, // simple
		object15, // simple
		object15, // simple		
		object18, // ud
		object18, // ud
		object18, // ud
		object18, // ud
		object03, // crc
		object03, // crc
		object03, // crc
		object03, // crc
		object08, // lcdnum
		object08, // lcdnum
		object10, // minver 
		object10, // minver 
		object10, // minver 
		object10, // minver 
		object04, // expint
		object04, // expint
		object14, // select
	}
};

/**
 * Entry point for core 2
 */
int
ep_core2(int hartid) {
	ep_dispatch(hartid, fjnodes, pnodes);
}
