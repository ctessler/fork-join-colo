PFX=riscv32-elf
CC=$(PFX)-cc
LD=$(PFX)-ld
CFLAGS=-O0 -g

exec_srcs = $(wildcard exec?.c)

all: riscv32-img riscv32-virt.dts 

riscv32-img: CFLAGS=-O0 -g3 -gdwarf-2 -ffreestanding -Wl,--gc-sections \
	-nostartfiles -nostdlib -nodefaultlibs -Wl,-Triscv32-virt.ld 
riscv32-img: image.c $(exec_srcs) crt0.s
	$(CC) $(CFLAGS) $? -o $@

riscv32.dtb:
	qemu-system-riscv32 -machine virt -m 128 -smp 4 -machine dumpdtb=riscv32.dtb

riscv32-virt.dts: riscv32.dtb
	dtc -I dtb -O dts -o riscv32-virt.dts riscv32.dtb

clean:
	rm -rf riscv32-img
	rm -rf riscv32.dtb riscv32-virt.dts
	rm -rf cache.log
