#include "config.h"
#include "objects.h"

object_t *fjnodes1[NUM_SECTIONS + 1] = {
	object01, // bs
	object15  // simple
};

object_t *pnodes1[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object13, // qurt
		object10, // minver
		object04, // expint
		object15, // simple
		object09, // matmult
		object09, // matmult
		object18, //ud
		object16, // sqrt
		object11, // ns
		object06, // insertsort
		object02, // bsort100
		object17, // statemate
	}
};

object_t *fjnodes2[NUM_SECTIONS + 1] = {
};

object_t *pnodes2[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object13, // qurt
		object10, // minver
		object04, // expint
		object15, // simple
		object09, // matmult
		object09, // matmult
		object18, // ud
		object16, // sqrt
		object11, // ns
		object06, // insertsort
		object02, // bsort
		object17, // statemate
	}
};

object_t *fjnodes3[NUM_SECTIONS + 1] = {
};
object_t *pnodes3[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
    {
	    object14, // select
	    object13, // qurt
	    object13, // qurt
	    object04, // expint
	    object04, // expint
	    object15, // simple
	    object09, // matmult
	    object01, // bs
	    object01, // bs
	    object01, // bs
	    object01, // bs
	    object18, // ud
	    object18, // ud
	    object16, // sqrt
	    object06, // insertsort
	    object06, // insertsort
	    object02, // bsort100
	    object17, // statemate
    }
};

object_t *fjnodes4[NUM_SECTIONS + 1] = {
};
object_t *pnodes4[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object13, // qurt
		object04, // expint
		object04, // expint
		object15, // simple
		object09, // matmult
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object18, // ud
		object18, // ud
		object16, // sqrt
		object06, // insertsort
		object02, // bsort100
		object17, // statemate
		object17, // statemate
	}
};

object_t *fjnodes5[NUM_SECTIONS + 1] = {
};
object_t *pnodes5[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object13, // qurt
		object04, // expint
		object15, // simple
		object15, // simple
		object09, // matmult
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object01, // bs
		object18, // ud
		object16, // sqrt
		object16, // sqrt
		object11, // ns
		object02, // bsort100
		object17, // statemate
		object17, // statemate
	}
};

object_t *fjnodes6[NUM_SECTIONS + 1] = {
};
object_t *pnodes6[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{
		object14, // select
		object13, // qurt
		object10, // minver
		object10, // minver
		object10, // minver
		object04, // expint
		object15, // simple
		object09, // matmult
		object09, // matmult
		object18, // ud
		object16, // sqrt
		object16, // sqrt
		object06, // insertsort
		object02, // bsort100
		object17, // statemate
		object17, // statemate
	}
};

object_t *fjnodes7[NUM_SECTIONS + 1] = {
};
object_t *pnodes7[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
    	object14, // select
		object13, // qurt
		object10, // minver
		object10, // minver
		object10, // minver
		object04, // expint
		object15, // simple
		object09, // matmult
		object09, // matmult
		object18, // ud
		object16, // sqrt
		object11, // ns
		object06, // insertsort
		object02, // bsort100
		object17, // statemate
};
