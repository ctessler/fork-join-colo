/**
 * Terribly inefficient implementation of memset
 *
 * Fills the first n bytes of the memory area pointed to by s with the
 * constant byte c
 */
void*
memset(void *s, int c, int n) {
	char *blck = (char *)s;
	for (int i=0; i<n; i++) {
		blck[i] = c;
	}
}
