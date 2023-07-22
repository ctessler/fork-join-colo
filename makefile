
all-tiny: evaluation_tiny simulation artifacts.pdf 
all-small: evaluation_small simulation artifacts.pdf 


clean: cleaner

evaluation_tiny:
	$(MAKE) -f gen.mk tiny -C ./eval/
	
evaluation_small:
	$(MAKE) -f gen.mk small -C ./eval/


cleaner:
	rm -r -f graphs
	rm -f artifacts.pdf
	$(MAKE) clean -C ./simul/
	$(MAKE) -f gen.mk clean -C ./eval/

simulation:
	$(MAKE) -C ./simul/ all

artifacts.pdf: 
	./simul/export.sh artifacts $(shell pwd)
	./eval/export.sh artifacts $(shell pwd)
	cp graph-tmplt.tex ./graphs/graph.tex
	sed -i -e '50 e cat ./graphs/mrtc-base-incr.tex' ./graphs/graph.tex
	cd ./graphs && latexmk -pdf graph.tex && latexmk -c
	mv ./graphs/graph.pdf artifacts.pdf
