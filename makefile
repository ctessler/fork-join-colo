subs=simul
.PHONY: $(subs)

all: tgt=all
all: evaluation $(subs) artifacts.pdf 

clean: tgt=clean
clean: $(subs) evaluation
	rm -r graphs
	rm artifacts.pdf

evaluation:
	$(MAKE) -f gen.mk -C ./eval/ $(tgt)

$(subs):
	echo "Made Subs"
	$(MAKE) -C $@ $(tgt)

artifacts.pdf: 
	./simul/export.sh artifacts $(shell pwd)
	./eval/export.sh artifacts $(shell pwd)
	cp graph-tmplt.tex ./graphs/graph.tex
	sed -i -e '57 e cat ./graphs/mrtc-base-incr.tex' ./graphs/graph.tex
	cd ./graphs && latexmk -pdf graph.tex && latexmk -c
	mv ./graphs/graph.pdf artifacts.pdf

