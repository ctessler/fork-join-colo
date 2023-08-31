PATH  := $(PATH):$(PWD)/bin
PYTHONPATH :=$(PYTHONPATH):$(PWD)/python-libs/


tiny:
	rm -r -f all-tiny
	gen-context.py -S 3 -O 5 -R 10 -D 200 -B 10 -I 10 -t 50 -A 0 -c all-tiny.json
	./go.sh -M 5 all-tiny.json all-tiny

small:
	rm -r -f all-small
	gen-context.py -S 5 -O 15 -R 15 -D 500 -t 1000 -B 50 -I 50 -A 0 -c all-small.json
	./go.sh -M 8 all-small.json all-small

group-e:
	rm -r -f group-e
	./go.sh -M 5 -U 100 ctxs/all-M5.json group-e

group-x:
	rm -r -f group-x
	./go.sh -M 64 -U 500 -X ctxs/approx-m64-u500.json group-x

clean:
	rm -f *.json
	rm -r -f all-tiny
	rm -r -f all-small
	rm -r -f group-e
	rm -r -f group-x