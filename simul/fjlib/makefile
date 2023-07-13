PFX=riscv32-unknown-elf
CC=$(PFX)-gcc
AS=$(PFX)-as
INCLUDE=inc
CFLAGS=-I$(INCLUDE) -O0 -g3 -gdwarf-2 -ffreestanding -nostartfiles \
	-nostdlib -nodefaultlibs -fno-tree-loop-distribute-patterns \
	-fno-builtin 
LIB=ar -rcs
ALG=$(shell basename $(shell pwd))
OBJDIR=obj
OBJECTS=$(patsubst src/%.c,${OBJDIR}/%.o, $(wildcard src/*.c))
ASMOBJS=$(patsubst asm/%.s,${OBJDIR}/%.o, $(wildcard asm/*.s))


all: libfj.a

$(OBJECTS): ${OBJDIR}/%.o : src/%.c | ${OBJDIR}
	$(CC) $(CFLAGS) -c $< -o $@

$(ASMOBJS): ${OBJDIR}/%.o : asm/%.s | ${OBJDIR}
	$(AS) $< -o $@

${OBJDIR}:
	mkdir ${OBJDIR}

libfj.a: $(OBJECTS) $(ASMOBJS) 
	$(LIB) $@ $(OBJECTS) $(ASMOBJS) 

clean:
	rm -rf libfj.a
	rm -rf ${OBJDIR}

