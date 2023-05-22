#include "ep.h"
#include "objects.h"


/**
 * Entry point for core 3
 */
int
ep_core3(int hartid) {
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


	/* fork-join node preceding section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* parallel section 2 */
	EC_READY(hartid);
	EC_START(hartid);
	object_c();
	object_c();	

	/* terminal fork-join node */
	EC_READY(hartid);
	EC_START(hartid);
	/* do nothing */

	/* ready to terminate */
	EC_READY(hartid);
}
