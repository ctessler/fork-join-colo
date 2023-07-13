#ifndef __EP_H__
#define __EP_H__
#include "config.h"
#include "lock-step.h"
#include "objects.h"

/**
 * @file ep.h
 *
 * Entry points for each of the cores
 */
int ep_control(int);
int ep_core1(int);
int ep_core2(int);
int ep_core3(int);
int ep_core4(int);
int ep_core5(int);
int ep_core6(int);
int ep_core7(int);

void ep_dispatch(int hartid, object_t **fjnodes,
		 object_t *pnodes[][MAX_SEC_THREADS + 1]);
int ep_stop(int);
int ep_ph2(int);
int ep_ph1(int);


#endif /* __EP_H__ */
