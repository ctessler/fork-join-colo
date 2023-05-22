#include "config.h"
#include "ep.h"

/**
 * The controller loop
 */
int
ep_control(int hartid) {
	for (int i=0; i < (2 * NUM_SECTIONS) + 1; i++) {
		/* A section (fork-join or parallel) */
		CC_ALL_READY();
		CC_START_ALL();
		CC_ALL_DONE();
	}
	/* wait to terminate */
	CC_EXIT();
}
