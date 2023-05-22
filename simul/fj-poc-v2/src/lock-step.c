#include "lock-step.h"

/* Global variables needed for the lock-step protocol */
unsigned int __LS_READY[NUM_CORES];
unsigned int __LS_STARTED[NUM_CORES];


/**
 * The controller core invokes this macro to signal the other cores to
 * proceed. Will block until all execution cores are LS_READY to
 * proceed.
 */
void
CC_SIGNAL() {
	int exe_core = 1;
check_ready:
	INT_PEND_CLEAR(0);
	while (__LS_READY[exe_core]) {
		__LS_STARTED[exe_core] = 0;
		exe_core++;
	}
	if (exe_core < NUM_CORES) {
		WFI;
		goto check_ready;
	}
	for (exe_core = 1; exe_core < NUM_CORES; exe_core++) {
		MSIP(exe_core) = 1;
	}
}

/**
 * Exits (shutsdown) the entire system.
 */
void
CC_EXIT() {
	int exe_core = 1;
check_ready:
	INT_PEND_CLEAR(0);
	while (__LS_READY[exe_core]) {
		__LS_STARTED[exe_core] = 0;
		exe_core++;
	}
	if (exe_core < NUM_CORES) {
		WFI;
		goto check_ready;
	}
	EXIT;
}

/**
 * The controller invokes this macro to reset the signal. Will block
 * until all execution cores have EC_START()'d
 */
void
CC_RESET() {
	int exe_core = 1;
check_ready:
	INT_PEND_CLEAR(0);
	while (__LS_STARTED[exe_core]) {
		exe_core++;
	}
	if (exe_core < NUM_CORES) {
		WFI;
		goto check_ready;
	}
}	
