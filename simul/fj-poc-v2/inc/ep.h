#ifndef __EP_H__
#define __EP_H__
#include "config.h"
#include "lock-step.h"


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


#endif /* __EP_H__ */
