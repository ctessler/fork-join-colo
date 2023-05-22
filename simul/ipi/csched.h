#ifndef __CSCHED__
#define __CSCHED__

/**
 * @file
 *
 * Header file to define the entry points for each of the core
 * schedules.
 *
 * This is a slapdash effort, things will be hardcoded.
 */

/**
 * Core schedule entry point function pointer
 *
 * (looks a lot like a main)
 */
typedef int (csched_t)(int hartid);

csched_t exec1;
csched_t exec2;
csched_t exec3;
csched_t exec4;
csched_t exec5;
csched_t exec6;
csched_t exec7;

#endif /* __CSCHED__ */
