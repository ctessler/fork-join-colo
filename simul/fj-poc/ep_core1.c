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
	object_a();

	/* parallel section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	object_b();
	object_c();


	/* fork-join node preceding section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	object_e();

	/* parallel section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	object_d();
	object_b();

	/* terminal fork-join node */
	EC_READY(hartid);
	EC_START(hartid);
	object_c();

	/* ready to terminate */
	EC_READY(hartid);
}
