#include "lock-step.h"

/* Global variables needed for the lock-step protocol */
unsigned int __LS_READY[NUM_CORES];
unsigned int __LS_START[NUM_CORES];
unsigned int __LS_DONE[NUM_CORES];

/**
 * The controller core invokes this function to wait for all cores to
 * be READY
 */
void
CC_ALL_READY() {
	int coreid = 1;
check_ready:
	INT_PEND_CLEAR(0);
	while (__LS_READY[coreid]) {
		coreid++;
	}
	if (coreid < NUM_CORES) {
		WFI;
		goto check_ready;
	}
}

/**
 * The controll core invokes this function to wait for all cores to
 * finish their current section.
 */
void
CC_ALL_DONE() {
	int coreid=1;
check_ready:
	INT_PEND_CLEAR(0);
	while (__LS_DONE[coreid]) {
		coreid++;
	}
	if (coreid < NUM_CORES) {
		WFI;
		goto check_ready;
	}
}

/**
 * The controller core invokes this function to signal cores to start
 * their next parallel section
 */
void
CC_START_ALL() {
	for (int coreid = 1; coreid < NUM_CORES; coreid++) {
		__LS_START[coreid] = 1;
		__LS_DONE[coreid] = 0;
		__LS_READY[coreid] = 0;
	}
	/* Signal ONLY after setting the new state */
	for (int coreid = 1; coreid < NUM_CORES; coreid++) {
		MSIP(coreid) = 1;
	}
}



/**
 * Exits (shutsdown) the entire system.
 *
 * Only invoked by the controller core
 */
void
CC_EXIT() {
	int coreid = 1;
check_ready:
	INT_PEND_CLEAR(0);
	while (__LS_READY[coreid]) {
		coreid++;
	}
	if (coreid < NUM_CORES) {
		WFI;
		goto check_ready;
	}
	EXIT;
}

/**
 * EC_READY
 *
 * Execution cores invoke this macro when they are ready to proceed.
 */
void
EC_READY(int coreid) {
	__LS_READY[coreid] = 1;
	__LS_START[coreid] = 0;
	INT_PEND_CLEAR(coreid);
	MSIP(0) = 1;
}

/**
 * EC_WAIT_START
 *
 * Execution cores call this function to wait until they are signalled
 * they are ready to start.
 */
void
EC_WAIT_START(int coreid) {
check_started:
	INT_PEND_CLEAR(0);
	if (!__LS_START[coreid]) {
		WFI;
		goto check_started;
	}
}

/**
 * EC_DONE
 *
 * Execution cores invoke this macro when they are done with a
 * parallel section
 */
void
EC_DONE(int coreid) {
	__LS_DONE[coreid] = 1;
	INT_PEND_CLEAR(coreid);
	MSIP(0) = 1;
}
