#include "objects.h"
#include "rv.h"

/**
 * @file objects.h
 *
 * Defines the objects used in the fork-join task
 */

void
object_a() {
	/* 128 noops, none repeated */
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
	PADOP;
}

void
object_b() {
	/* 128 noops, 64 repeated */
	for (int i=0; i<2; i++) {
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
	}
}

void
object_c() {
	/* 128 nops, 96 repeated */
	for (int i=0; i<4; i++) {
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
	}
}

void
object_d() {
	/* 128 nops, 112 repeated */
	for (int i=0; i<8; i++) {
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
		PADOP;
	}
}

void
object_e() {
	/* 128 nops, 127 repeated */
	for (int i=0; i<128; i++) {
		PADOP;
	}
}
