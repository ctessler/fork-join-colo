.PHONY: $(GRAPHDIR)/graphs.pdf
TMPLT := tmplt/graph-tmplt.tex

SCALED := $(shell [ -e $(GRAPHDIR)/1.00Y ] && echo 1 || echo 0)
DSTDIR := $(GRAPHDIR)/graphs

ifeq ($(SCALED), 1)
	TMPLT := tmplt/scaled-tmplt.tex
endif 

all: $(DSTDIR)/graphs.pdf

$(DSTDIR)/graphs.pdf:
	echo $(TMPLT)
	cp $(TMPLT) $(DSTDIR)/graph.tex
	cd $(DSTDIR) && latexmk -pdf graph.tex && latexmk -c

