#include "objects.h"
#include "rv.h"

/**
 * @file
 *
 * Port of the MRTC benchmark sqrt
 */

/* MDH WCET BENCHMARK SUITE. File version $Id: sqrt.c,v 1.1.1.1 2007-12-11 15:22:56 puaut Exp $ */

/*************************************************************************/
/*                                                                       */
/*   SNU-RT Benchmark Suite for Worst Case Timing Analysis               */
/*   =====================================================               */
/*                              Collected and Modified by S.-S. Lim      */
/*                                           sslim@archi.snu.ac.kr       */
/*                                         Real-Time Research Group      */
/*                                        Seoul National University      */
/*                                                                       */
/*                                                                       */
/*        < Features > - restrictions for our experimental environment   */
/*                                                                       */
/*          1. Completely structured.                                    */
/*               - There are no unconditional jumps.                     */
/*               - There are no exit from loop bodies.                   */
/*                 (There are no 'break' or 'return' in loop bodies)     */
/*          2. No 'switch' statements.                                   */
/*          3. No 'do..while' statements.                                */
/*          4. Expressions are restricted.                               */
/*               - There are no multiple expressions joined by 'or',     */
/*                'and' operations.                                      */
/*          5. No library calls.                                         */
/*               - All the functions needed are implemented in the       */
/*                 source file.                                          */
/*                                                                       */
/*                                                                       */
/*************************************************************************/
/*                                                                       */
/*  FILE: my_sqrt.c                                                         */
/*  SOURCE : Public Domain Code                                          */
/*                                                                       */
/*  DESCRIPTION :                                                        */
/*                                                                       */
/*     Square root function implemented by Taylor series.                */
/*                                                                       */
/*  REMARK :                                                             */
/*                                                                       */
/*  EXECUTION TIME :                                                     */
/*                                                                       */
/*                                                                       */
/*************************************************************************/

/* Changes: Indented program. Added a main program. Changed fabs and my_sqrt to fabs and my_sqrt.
 */


float           my_fabs(float x);
float           my_sqrt(float val);

float object(1)
my_fabs(float x)
{
	if (x < 0)
		return -x;
	else
		return x;
}

float object(1)
my_sqrt(float val)
{
	float           x = val / 10;

	float           dx;

	double          diff;
	double          min_tol = 0.00001;

	int             i, flag;

	flag = 0;
	if (val == 0)
		x = 0;
	else {
		for (i = 1; i < 20; i++) {
		  if (!flag) {
		    dx = (val - (x * x)) / (2.0 * x);
		    x = x + dx;
		    diff = val - (x * x);
		    if (my_fabs(diff) <= min_tol)
		      flag = 1;
		  } else
		    x = x;
		}
	}
	return (x);
}

void object(1)
object01()
{
	my_sqrt(19.5);
}
