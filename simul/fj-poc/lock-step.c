#include "lock-step.h"

/* Global variables needed for the lock-step protocol */
unsigned int __LS_SIGNAL=0;
unsigned int __LS_READY[NUM_CORES];
unsigned int __LS_STARTED[NUM_CORES];


