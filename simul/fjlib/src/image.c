#include "config.h"
#include "rv.h"

extern ep_t* ENTRY_POINTS[NUM_CORES];
/**
 * Shared entry point by each core.
 */
int
main(int argc, char** argv) {
	int *hartid;
	READ_GP(hartid);

	/* Vector to core specific entry point */
	ENTRY_POINTS[*hartid](*hartid);

	/* Core 0 is the only one that should reach this point */
	EXIT;
};
