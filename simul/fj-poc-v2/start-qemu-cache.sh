QEMU=${QEMU:-/home/ct/ws/riscv-fs/qemu/qemu.git/build/qemu-system-riscv32}
PLUGIN=${PLUGIN:-/home/ct/ws/riscv-fs/qemu/qemu.git/build/contrib/plugins/libcache.so}

opts=-nographic 	# disable the graphical output
opts+=" -machine virt"	# the RISC-V simulated machine
opts+=" -bios none"	# Prevent the OpenSBI bios from being loaded
opts+=" -m 128M"	# 128 megabytes of memory
opts+=" -S"		# freeze the CPU on startup
opts+=" -s"		# "shorthand" for "-gdb tcp:1234"
opts+=" -smp 8"		# The number of cores (harts)
# The -gdb option does not work, I do not know why
# opts+=" -gdb tcp:4321"	# Specify the GDB remote port

# libcache enable and parameters
opts+=" --plugin ${PLUGIN}"
opts+=',dcachesize=8192,dassoc=2,dblksize=64'
opts+=',icachesize=8192,iassoc=2,iblksize=64'
opts+=' -d plugin'
opts+=' -D cache.log'

opts+=" -kernel $1"	# the kernel to add

echo "Invoking: ${QEMU} ${opts}"
${QEMU} ${opts}
