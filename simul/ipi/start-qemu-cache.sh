QEMU=${QEMU:-/home/ct/bin/qemu-8.0.0/bin/qemu-system-riscv32}

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
opts+=' --plugin /home/ct/bin/qemu-8.0.0/contrib/plugins/libcache.so'
#opts+=',dcachesize=8192,dassoc=4,dblksize=64'
#opts+=',dcachesize=0,dassoc=0,dblksize=0'
opts+=',icachesize=8192,iassoc=4,iblksize=64'
opts+=' -d plugin'
opts+=' -D cache.log'

opts+=" -kernel $1"	# the kernel to add

echo "Invoking: ${QEMU} ${opts}"
${QEMU} ${opts}
