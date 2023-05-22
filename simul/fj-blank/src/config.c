#include "config.h"
#include "ep.h"

ep_t* ENTRY_POINTS[NUM_CORES] = {
	ep_control, // core 0
	ep_core1,
	ep_core2,
	ep_core3,
	ep_core1,
	ep_core1,
	ep_core1,
	ep_core1
};
