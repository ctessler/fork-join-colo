#include "ep.h"
#include "objects.h"

/**
 * Entry point for core 1
 */
int
ep_core1(int hartid) {
	/* By convention core 1 executes all fork and join nodes */

	/* fork-join node preceding section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* parallel section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	object_a();
	object_b();

        object_a();
	object_b();

        object_a();
	object_b();	

	object_a();
	object_b();

        object_a();
	object_b();

        object_a();
	object_b();	

	/* terminal fork-join node */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* ready to terminate */
	EC_READY(hartid);
}
