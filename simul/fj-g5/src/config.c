#include "config.h"
#include "ep.h"

ep_t* ENTRY_POINTS[NUM_CORES] = {
	ep_control, // core 0
	ep_core1,
	ep_core2,
	ep_core3,
	ep_core4,
	ep_core5,
	ep_core6,
	ep_ph2
};
