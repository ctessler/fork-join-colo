#include "config.h"
#include "objects.h"

object_t *fjnodes1[NUM_SECTIONS + 1] = {
};

object_t *pnodes1[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
{object01}
};

object_t *fjnodes2[NUM_SECTIONS + 1] = {
};

object_t *pnodes2[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{NULL},
	{object01, object01}
};

object_t *fjnodes3[NUM_SECTIONS + 1] = {
};
object_t *pnodes3[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object02}
};

object_t *fjnodes4[NUM_SECTIONS + 1] = {
};
object_t *pnodes4[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{NULL},
	{object02, object02}
};

object_t *fjnodes5[NUM_SECTIONS + 1] = {
};
object_t *pnodes5[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{object03}
};

object_t *fjnodes6[NUM_SECTIONS + 1] = {
};
object_t *pnodes6[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
	{NULL},
	{object03, object03}
};

object_t *fjnodes7[NUM_SECTIONS + 1] = {
};
object_t *pnodes7[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {
};
