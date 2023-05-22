#include "config.h"
#include "ep.h"

/**
 * The controller loop
 */
int
ep_control(int hartid) {
	for (int s=0; s < (2 * NUM_SECTIONS) + 1; s++) {
		CC_READY();
		CC_DONE();
	}
	CC_EXIT();
}
