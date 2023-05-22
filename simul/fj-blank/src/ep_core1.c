#include "ep.h"
#include "objects.h"


/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	/* Source Fork-Join Node */
	EC_READY(hartid);
	EC_WAIT_START(hartid);
	/*
	 * Call fork-join node method
	 */
	EC_DONE(hartid);

	/* Parallel Section 1 */
	EC_READY(hartid);
	EC_WAIT_START(hartid);
	/*
	 * Call seciton 1
	 */
	EC_DONE(hartid);

	/* Terminal Fork-Join Node */
	EC_READY(hartid);
	EC_WAIT_START(hartid);
        /*
	 * Call fork-join node method
	 */
	EC_DONE(hartid);

	/* Nothing more to do, just stall */
	EC_READY(hartid);
	WFI;
}
