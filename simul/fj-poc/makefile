PFX=riscv32-elf
CC=$(PFX)-cc
LD=$(PFX)-ld
AS=$(PFX)-as
LDFLAGS=--gc-sections -Triscv32-virt.ld
CFLAGS=-O0 -g3 -gdwarf-2 -ffreestanding -nostartfiles -nostdlib -nodefaultlibs

core_objs = $(patsubst %.c,%.o, $(wildcard ep_core*.c))
config_objs = config.o
lockstep_objs = lock-step.o

all: riscv32-img

riscv32-img: image.o crt0.o $(core_objs) $(config_objs) \
	$(lockstep_objs) objects.o ep_control.o
	$(LD) $(LDFLAGS) $? -o $@

riscv32.dtb:
	qemu-system-riscv32 -machine virt -m 128 -smp 4 -machine dumpdtb=riscv32.dtb

riscv32-virt.dts: riscv32.dtb
	dtc -I dtb -O dts -o riscv32-virt.dts riscv32.dtb

clean:
	rm -rf riscv32-img riscv32-img-debug
	rm -rf riscv32.dtb riscv32-virt.dts
	rm -rf cache.log
	rm -rf *.o
	rm -rf *~ *-exp.c

