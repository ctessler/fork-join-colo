subs=2-Gram 3-Parm 3-Parm-HD
task=$(shell basename $(shell pwd))
.PHONY: $(subs) graphs

all: tgt=all
all: $(subs) data.csv graphs

clean: tgt=clean
clean: $(subs)
	echo "Cleaning $<"
	rm -f data.csv
	rm -rf graphs

data.csv: $(subs)
	cp 2-Gram/data.csv .
	tail -n1 3-Parm/data.csv >> data.csv
	tail -n1 3-Parm-HD/data.csv >> data.csv

graphs: data.csv
	mkdir -p graphs
	../bin/poc-graph.py data.csv
	rename mrtc $(task) *.png *.eps
	mv *.png *.eps graphs/.


$(subs):
	$(MAKE) -C $@ $(tgt)
