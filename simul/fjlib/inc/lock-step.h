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

void EC_READY(int hartid);
void EC_DONE(int hartid);

void CC_READY(void);
void CC_DONE(void);

void CC_EXIT(void);

#endif /* __LOCK_STEP_H__ */
