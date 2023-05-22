#ifndef __LOCK_STEP_H__
#define __LOCK_STEP_H__
#include "rv.h"

/**
 * @file
 *
 * The 'lockstep' protocol for fork-join tasks
 *
 * PSEUDOCODE of the protocol
 *
 * From the controller:

 control:
    for reps in portions :
        wait for all execution cores to be ready
	signal cores to proceed
	wait for all execution cores to signal they have started

 * From the execution cores
 execution:
    for reps in portions :
	send the ready to execute next portion message
	wait for signal to proceed
	send the starting portion message
	execute portion
    
 * Implementation

 control() {
     for (int reps=0; reps < PORTIONS; reps++) {
         CC_SIGNAL();
	 CC_RESET();
     }

 exec_core() {
     coreid = hartid;
     for (int reps=0; reps < PORTIONS; reps++) {
         EC_READY(coreid);
	 EC_START(coreid);
	 do_stage(reps);
     }
 */

/**
 * @define NUM_CORES the number of cores in the system.
 */
#ifndef NUM_CORES
#define NUM_CORES 8
#endif

/**
 * @define __LS_SIGNAL
 *
 * Setting this value to non-zero instructs the execution cores to
 * move to the next portion of their schedule.
 */
extern unsigned int __LS_SIGNAL;

/**
 * @define __LS_READY
 *
 * Setting the i'th value to non-zero indicates to the controller core
 * the i'th core is ready to move to the next portion of their
 * schedule.
 */
extern unsigned int __LS_READY[NUM_CORES];

/**
 * @define __LS_STARTED
 *
 * Setting the i'th value to non-zero indicates to the controller core
 * the i'th core has started executing
 */
extern unsigned int __LS_STARTED[NUM_CORES];

/**
 * @define EC_READY
 *
 * Execution cores invoke this macro when they are ready to proceed,
 * this will block (spin-lock) until the controller signals alls cores
 * to proceed. 
 */
#define EC_READY(core_id) do {			\
	INT_PEND_CLEAR(core_id);		\
	__LS_READY[core_id] = 1;		\
	WFI;					\
	INT_PEND_CLEAR(core_id);		\
} while (0)

/**
 * @define EC_START(core_id)
 *
 * Execution cores invoke this macro when they begin executing their
 * next portion
 */
#define EC_START(core_id) do {			\
	__LS_READY[core_id] = 0;		\
	__LS_STARTED[core_id] = 1;		\
} while (0)

/**
 * @define CC_SIGNAL
 *
 * The controller core invokes this macro to signal the other cores to
 * proceed. Will block until all execution cores are LS_READY to
 * proceed.
 *
 * @todo: This could be improved by using the MSI interrupt for the
 * controller core, e.g. core 1 sets MSIP(0) = 1, causing core 0 to
 * check if all cores are ready.
 */
#define CC_SIGNAL(unused) do {				\
	int __lss_i = 1;				\
	while (__lss_i < NUM_CORES) {			\
		if (__LS_READY[__lss_i]) {		\
			__LS_STARTED[__lss_i] = 0;	\
			__lss_i++;			\
		}					\
	}						\
	__LS_SIGNAL = 1;				\
	for (__lss_i = 1; __lss_i < NUM_CORES;		\
	     __lss_i++) {				\
		MSIP(__lss_i) = 1;			\
	}						\
} while(0)

/**
 * @define CC_RESET
 *
 * The controller invokes this macro to reset the signal. Will block
 * until all execution cores have EC_START()'d
 *
 * XXX
 * @todo a busy loop, this could be improved with software interrupts
 * XXX
 */
#define CC_RESET(unused) do {			\
	int __lss_i = 1;			\
	while (__lss_i < NUM_CORES) {		\
		if (__LS_STARTED[__lss_i]) {	\
			__lss_i++;		\
		}				\
	}					\
	__LS_SIGNAL = 0;			\
} while(0)



#endif /* __LOCK_STEP_H__ */
