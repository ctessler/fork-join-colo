PATH  := $(PATH):$(PWD)/bin
PYTHONPATH :=$(PYTHONPATH):$(PWD)/python-libs/

all: evaluation

evaluation:
	gen-context.py -S 3 -O 5 -R 10 -D 200 -B 10 -I 10 -t 50 -A 0 -c all-tiny.json
	./go.sh -M 5 all-tiny.json all-tiny

clean:
	rm *.json
	rm -r all-tiny
