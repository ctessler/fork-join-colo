PFX=riscv32-elf
CC=$(PFX)-cc
LD=$(PFX)-ld
CFLAGS=-O0 -g

all: riscv32-img 

riscv32-img: CFLAGS=-O0 -g3 -gdwarf-2 -ffreestanding -Wl,--gc-sections \
	-nostartfiles -nostdlib -nodefaultlibs -Wl,-Triscv32-virt.ld 
riscv32-img: image.c crt0.s
	$(CC) $(CFLAGS) $? -o $@

clean:
	rm -rf riscv32-img 
	rm -rf cache.log

