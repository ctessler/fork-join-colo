#include "ep.h"
#include "objects.h"


/**
 * Entry point for core 7
 */
int
ep_core7(int hartid) {
	/* By convention core 1 executes all fork and join nodes */

	/* fork-join node preceding section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* parallel section 1 */
	EC_READY(hartid);
	EC_START(hartid);
	object_d();


	/* fork-join node preceding section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* parallel section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	object_a();
	object_a();	

	/* terminal fork-join node */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* ready to terminate */
	EC_READY(hartid);
}
