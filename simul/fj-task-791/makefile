subs=2gram 3parm 3parmhd

.PHONY: $(subs)

all: tgt=all
all: $(subs) data.csv

clean: tgt=clean
clean: $(subs)
	echo "Cleaning $<"
	rm -f data.csv

data.csv: $(subs)
	cp 2gram/data.csv .
	tail -n1 3parm/data.csv >> data.csv
	tail -n1 3parmhd/data.csv >> data.csv

$(subs):
	$(MAKE) -C $@ $(tgt)
