PFX=riscv32-unknown-elf
CC=$(PFX)-gcc
LD=$(PFX)-ld
LIBPATH=../../../fjlibgroup/
LIB=-L$(LIBPATH) -lfj
AS=$(PFX)-as
INCLUDE=../../../fjlibgroup/inc
LDFLAGS=--gc-sections -T$(LIBPATH)riscv32-virt.ld
CFLAGS=-I$(INCLUDE) -O0 -g3 -gdwarf-2 -ffreestanding -nostartfiles \
	-nostdlib -nodefaultlibs -fno-tree-loop-distribute-patterns \
	-fno-builtin

ALG=$(shell basename $(shell pwd))
OBJDIR=obj
OBJECTS=$(patsubst src/%.c,${OBJDIR}/%.o, $(wildcard src/*.c))
ASMOBJS=$(patsubst asm/%.s,${OBJDIR}/%.o, $(wildcard asm/*.s))


all: riscv32-img cache.log

$(OBJECTS): ${OBJDIR}/%.o : src/%.c | ${OBJDIR}
	$(CC) $(CFLAGS) -c $< -o $@

${OBJDIR}:
	mkdir ${OBJDIR}

riscv32-img: $(OBJECTS)
	$(LD) $(LDFLAGS) $^ $(LIB) -o $@

cache.log: riscv32-img
	../../../bin/qemu.sh riscv32-img

data.csv: riscv32-img
	../../../bin/mqemu.py -f $(ALG) -v -i 100 riscv32-img

clean:
	rm -rf riscv32-img
	rm -rf ${OBJDIR}
	rm -rf cache.log
