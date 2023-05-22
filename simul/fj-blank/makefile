PFX=riscv32-elf
CC=$(PFX)-cc
LD=$(PFX)-ld
AS=$(PFX)-as
INCLUDE=inc
LDFLAGS=--gc-sections -Triscv32-virt.ld
CFLAGS=-I$(INCLUDE) -O0 -g3 -gdwarf-2 -ffreestanding -nostartfiles \
	-nostdlib -nodefaultlibs -fno-tree-loop-distribute-patterns \
	-fno-builtin

OBJDIR=obj
OBJECTS=$(patsubst src/%.c,${OBJDIR}/%.o, $(wildcard src/*.c))
ASMOBJS=$(patsubst asm/%.s,${OBJDIR}/%.o, $(wildcard asm/*.s))


all: riscv32-img

$(OBJECTS): ${OBJDIR}/%.o : src/%.c | ${OBJDIR}
	$(CC) $(CFLAGS) -c $< -o $@

$(ASMOBJS): ${OBJDIR}/%.o : asm/%.s | ${OBJDIR}
	$(AS) $< -o $@

${OBJDIR}:
	mkdir ${OBJDIR}

riscv32-img: $(OBJECTS) $(ASMOBJS)
	$(LD) $(LDFLAGS) $^ -o $@

clean:
	rm -rf riscv32-img
	rm -rf ${OBJDIR}

