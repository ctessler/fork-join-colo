subs=2gram 3parm 3parmhd

.PHONY: $(subs)

all: tgt=all
all: $(subs)

clean: tgt=clean
clean: $(subs)
	echo "Cleaning $<"


$(subs):
	$(MAKE) -C $@ $(tgt)
