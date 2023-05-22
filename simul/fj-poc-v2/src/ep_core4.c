#include "ep.h"
#include "objects.h"


/**
 * Entry point for core 4
 */
int
ep_core4(int hartid) {
	/* By convention core 1 executes all fork and join nodes */

	/* fork-join node preceding section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* parallel section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	object_a();


	/* fork-join node preceding section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* parallel section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	object_b();
	object_d();	

	/* terminal fork-join node */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* ready to terminate */
	EC_READY(hartid);
}
