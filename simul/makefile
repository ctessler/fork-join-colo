subs=fj-g1 fj-g2 fj-g3 fj-g4 fj-g5 fj-g6 fj-b1 fj-b2 \
     fj-task-94-2gram fj-task-94-3parm fj-task-94-3parm \
	fj-task-94-exactnocolo fj-task-94-exactcolo  \
     fj-task-273-2gram fj-task-273-3parm fj-task-273-3parmhd \
	fj-task-273-exactnocolo fj-task-273-exactcolo  \
     fj-task-346-2gram fj-task-346-3parm fj-task-346-3parmhd \
	fj-task-346-exactnocolo fj-task-346-exactcolo \
     fj-task-284-2gram fj-task-284-3parm fj-task-284-3parmhd \
     fj-task-752 fj-task-791 fj-task-956 fj-task-484

.PHONY: $(subs)

all: tgt=all
all: $(subs)

clean: tgt=clean
clean: $(subs)
	echo "Cleaning here"

$(subs):
	$(MAKE) -C $@ $(tgt)
