#include "lock-step.h"

/* Global variables needed for the lock-step protocol */

/**
 * EXECUTION CORES (ecores EC) set their coreid to a true value to indicate
 * they are ready to  progress to the next segment
 */
unsigned int __EC_READY[NUM_CORES];

/**
 * CONTROL CORES (ccores CC) sets this value to true to indicate that
 * *ALL* ECs are ready.
 */
unsigned int __CC_READY;

/**
 * EXECUTION CORES (ecores EC) set their coreid to a true value to
 * indicate they finished their last segment
 */
unsigned int __EC_DONE[NUM_CORES];

/**
 * CONTROL CORES (ccores CC) sets this value to a true value to
 * indicate that *ALL* ECs are done with their last segment.
 */
unsigned int __CC_DONE;

/**
 * CC_READY
 *
 * The CC calls this function to synchronize the readiness of all ECs
 *
 * This call will block until all ECs are ready
 */
void
CC_READY() {
	int coreid = 1;
check_ready:
	INT_PEND_CLEAR(0);
	/* An execution core cannot be readied twice without starting */
	while (__EC_READY[coreid]) {
		coreid++;
	}
	if (coreid < NUM_CORES) {
		WFI;
		goto check_ready;
	}
	/* All ECs are ready, wake them up */
	__CC_DONE = 0;
	__CC_READY = 1;
	for (int coreid = 1; coreid < NUM_CORES; coreid++) {
		MSIP(coreid) = 1;
	}
}

/**
 * EC_READY
 *
 * The ECs call this function to indicate their readiness, the call
 * returns when the CC has determined all ECs are ready to proceed.
 */
void
EC_READY(int coreid) {
	__EC_DONE[coreid] = 0;
	__EC_READY[coreid] = 1;
	MSIP(0) = 1;
check_ready:
	INT_PEND_CLEAR(coreid);
	if (!__CC_READY) {
		WFI;
		goto check_ready;
	}
	__EC_READY[coreid] = 0;
}

/**
 * CC_DONE
 *
 * The CC calls this function to synchronize the doneness of all ECs.
 *
 * This call will block until all ECs are done.
 */
void
CC_DONE(void) {
	int coreid = 1;
check_done:
	INT_PEND_CLEAR(0);
	while (__EC_DONE[coreid]) {
		coreid++;
	}
	if (coreid < NUM_CORES) {
		WFI;
		goto check_done;
	}
	/* All ECs are done, wake them up */
	__CC_READY = 0;
	__CC_DONE = 1;
	for (int coreid = 1; coreid < NUM_CORES; coreid++) {
		MSIP(coreid) = 1;
	}
}

/**
 * EC_DONE
 *
 * The ECs call this function to indicate their doneness, the call
 * returns when the CC has determined all ECs are done.
 */
void
EC_DONE(int coreid) {
	__EC_DONE[coreid] = 1;
	MSIP(0) = 1;
check_done:
	INT_PEND_CLEAR(coreid);
	if (!__CC_DONE) {
		MSIP(0) = 1;
		WFI;
		goto check_done;
	}
}

/**
 * CC_EXIT
 *
 * Terminates the entire system, invoked by the CC.
 */
void
CC_EXIT() {
	EXIT;
}

