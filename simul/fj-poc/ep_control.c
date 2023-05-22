#include "config.h"
#include "ep.h"

/**
 * The controller loop
 */
int
ep_control(int hartid) {
	/*
	 * There are NUM_SECTION parallel sections, there are then
	 * NUM_SECTION + 1 fork-join nodes
	 */
	for (int i=0; i < (2 * NUM_SECTIONS) + 1; i++) {
		/* XXX @todo: Print a status message
		 * "Section i, waiting for cores to finish previous
		 * section"
		 */
		/* When all cores are ready, signal them to start */
		CC_SIGNAL();

		/* XXX @todo: Print a status message
		 * "Section i, cores are ready, signalled to start"
		 */
		/* Block until all cores have started */
		CC_RESET();
	}
}
