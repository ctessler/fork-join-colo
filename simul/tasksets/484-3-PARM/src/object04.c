#include "objects.h"
#include "rv.h"

/**
 * @file
 *
 * Port of the MRTC expint benchmark
 */
/* MDH WCET BENCHMARK SUITE. File version $Id: expint.c,v 1.1.1.1 2007-12-11 15:22:55 puaut Exp $ */

/************************************************************************
 * FROM:
 *   http://sron9907.sron.nl/manual/numrecip/c/expint.c
 *
 * FEATURE:
 *   One loop depends on a loop-invariant value to determine
 *   if it run or not.
 *
 ***********************************************************************/

long int        object04_foo(long int x);
long int        expint(int n, long int x);

void object(4)
object04(void)
{
	expint(50, 1);
	/* with  expint(50,21) as argument, runs the short path */
	/* in expint.   expint(50,1)  gives the longest execution time */
}

long int object(4)
object04_foo(long int x)
{
	return x * x + (8 * x) << (4 - x);
}


/* Function with same flow, different data types,
   nonsensical calculations */
long int object(4)
expint(int n, long int x)
{
	int             i, ii, nm1;
	long int        a, b, c, d, del, fact, h, psi, ans;

	nm1 = n - 1;		/* arg=50 --> 49 */

	if (x > 1) {		/* take this leg? */
		b = x + n;
		c = 2e6;
		d = 3e7;
		h = d;

		for (i = 1; i <= 100; i++) {	/* MAXIT is 100 */
		  a = -i * (nm1 + i);
		  b += 2;
		  d = 10 * (a * d + b);
		  c = b + a / c;
		  del = c * d;
		  h *= del;
		  if (del < 10000) {
		    ans = h * -x;
		    return ans;
		  }
		}
	} else {		/* or this leg? */
		/* For the current argument, will always take */
		/* '2' path here: */
		ans = nm1 != 0 ? 2 : 1000;
		fact = 1;
		for (i = 1; i <= 100; i++) {	/* MAXIT */
		  fact *= -x / i;
		  if (i != nm1)	/* depends on parameter n */
		    del = -fact / (i - nm1);
		  else {	/* this fat piece only runs ONCE *//* runs on
								    * iter 49 */
		    psi = 0x00FF;
		    for (ii = 1; ii <= nm1; ii++)	/* */
		      psi += ii + nm1;
		      del = psi + fact * object04_foo(x);
		  }
		  ans += del;
		  /* conditional leave removed */
		}

	}
	return ans;
} 
