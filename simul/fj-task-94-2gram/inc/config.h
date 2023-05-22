#ifndef __CONFIG_H__
#define __CONFIG_H__

/**
 * @file config.h
 *
 * Parameters of the fork-join proof-of-concept execution.
 */

/**
 * @define NUM_SECTIONS
 *
 * The number of parallel sections in the application
 *
 * XXX
 * This should not be a static variable, this could be addressed with
 * a protocol extenion.
 * XXX
 */
#define NUM_SECTIONS 1

/**
 * @define MAX_SEC_THREADS
 *
 * The maximum number of threads per core schedule per parallel
 * section. For parallel section 5:

 core 1 schedule: a a a b b b c      [7 threads]
 core 2 schedule: a b a b c d e f    [8 threads]

 MAX_SEC_THREADS must be at least 8
*/
#define MAX_SEC_THREADS 64



/**
 * @define NUM_CORES
 *
 * The number of cores used by the system
 */
#define NUM_CORES 8


/**
 * Entry entry point function pointer
 */
typedef int (ep_t)(int hartid);

/**
 * Entry points for the cores
 *
 * XXX
 * This seems ripe for correction, some other method for finding (or
 * setting) the entry point for each core. It could be based on a
 * linker script or a stack value.
 *
 * As is, it requires careful manipulation of the data structures.
 * XXX
 */
extern ep_t *ENTRY_POINTS[NUM_CORES];

#define NULL 0

#endif /* __CONFIG_H__ */
