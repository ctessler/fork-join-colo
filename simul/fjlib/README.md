# FJLIB
FJLIB is a fork-join scheduling library. This folder contains the necessary files to make and compile the library. The library can be configured for fork-join tasks by modifying `config.h` and adjusting the number of sections, and max section of threads. An example of this modification can be found below:

~~~cpp
#ifndef __CONFIG_H__
#define __CONFIG_H__

/**
 * @file config.h
 *
 * Parameters of the fork-join proof-of-concept execution.
 */
/**
 * @define NUM_SECTIONS
 *
 * The number of parallel sections in the application
 *
 */
#define NUM_SECTIONS 1

/**
 * @define MAX_SEC_THREADS
 *
 * The maximum number of threads per core schedule per parallel
 * section. For parallel section 5:

 core 1 schedule: a a a b b b c      [7 threads]
 core 2 schedule: a b a b c d e f    [8 threads]

 MAX_SEC_THREADS must be at least 8
*/
#define MAX_SEC_THREADS 256

...
~~~

After doing so the library can be compiled with the `makefile` within the directory. 

```
make
```

# fjlib Contents 

`asm` - Assembly files necessary to compile the library. 
 - `crt0.s` - Custom setup c runtime file that setups the stack for each core.

`inc` - Include folder containing necessary headers to compile the library. Most headers contain just prototypes or declarations for their respective file. The `config.h` will need to be adjusted depending on the task and library recompiled. 

`src` - all c source files used to compile the library. 

- `ep.c` - pointer functions to each core entry point. 

- `ep_control.c` - File that handles entry point controls. 

- `ep_core1.c - ep_core7.c` - All entry points for all cores. Each entry point will be linked at compile time with their respective task objects. 

- `ep.c` - handles when each core schedule should be dispatched. 

- `image.c` - Reads each cores stack pointer to find the entry point of each core.

- `lock-step.c` - Handles the locking and releasing of each core. 

- `memcpy.c` - Copy memory from a location of n bytes. 

- `memset.c` - Fills a memory location with n bytes.

`makefile` - makefile that builds the library.  

`README.md` - source of this file.  

`riscv32-virt.ld` - custom linker script that places the objects and library in their own space of memory. 


