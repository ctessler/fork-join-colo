#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import logging

# Default Generation Values
DEFAULTS = {
    # The lower and upper bounds on the number of parallel sections 
    'SECTION-MIN' : 1,
    'SECTION-MAX' : 100,
    # The lower and upper bounds on the number objects across the
    # entire task
    'OBJECTS-MIN' : 1,
    'OBJECTS-MAX' : 100,
    # WCET(n) = BASE + n * INCREMENTAL
    # The lower and upper bounds on the BASE WCET of any object
    'BASE-MIN' : 1,
    'BASE-MAX' : 50,
    # The lower and upper bounds on the INCREMENTAL WCET of any object
    # Must allow for 0 in case there is no benefit
    'INCR-MIN' : 1,
    'INCR-MAX' : 50,
    # Upper and lower bounds on the deadline of any task
    'DEADLINE-MIN' : 1,
    'DEADLINE-MAX' : 10000,
    # Number of tasks to generate
    'TASKS' : 1000,
    # Number of task sets to generate
    'TASK-SETS' : 10000,
    # Lower bound on the number of tasks per task set
    'TASK-SET-SIZE-MIN' : 2,
    # Upper bound on the number of tasks per task set
    'TASK-SET-SIZE-MAX' : 100,
    # The number of threads per parallel section, represented as
    # multiple nodes of the same object i.e. nodes implicity represent
    # a single thread
    'THREADS-MIN': 1,
    'THREADS-MAX': 100
}

# Creates a parser with the arguments specific to this script
def gen_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-s', '--sections-lb', type=int,
                        default = DEFAULTS['SECTION-MIN'],
                        help='A lower bound on the number of parallel '
                        'sections for a task')
    parser.add_argument('-S', '--sections-ub', type=int,
                        default = DEFAULTS['SECTION-MAX'],
                        help='An upper bound on the number of '
                        'parallel sections for a task')
    parser.add_argument('-o', '--objects-lb', type=int,
                        default = DEFAULTS['OBJECTS-MIN'],
                        help='A lower bound on the number of objects '
                        'per task')    
    parser.add_argument('-O', '--objects-ub', type=int,
                        default = DEFAULTS['OBJECTS-MAX'],
                        help='An upper bound on the number of objects '
                        'per task')
    parser.add_argument('-r', '--threads-lb', type=int,
                        default = DEFAULTS['THREADS-MIN'],
                        help='A lower bound on the number of threads '
                        'per parallel section')
    parser.add_argument('-R', '--threads-ub', type=int,
                        default = DEFAULTS['THREADS-MAX'],
                        help='An upper bound on the number of threads '
                        'per parallel section')
    parser.add_argument('-d', '--deadline-lb', type=int,
                        default = DEFAULTS['DEADLINE-MIN'],
                        help='A lower bound on a tasks deadline')
    parser.add_argument('-D', '--deadline-ub', type=int,
                        default = DEFAULTS['DEADLINE-MAX'],
                        help='An upper bound on a tasks deadline')

    group = parser.add_argument_group('TASK Set Arguments')

    group.add_argument('-t', '--tasks', type=int,
                       default = DEFAULTS['TASKS'],
                       help="Number of individual tasks to generate")
    group.add_argument('-A', '--task-sets', type=int,
                        default = DEFAULTS['TASK-SETS'],
                        help="Number of task sets to generate")
    group.add_argument('-z', '--set-size-lb', type=int,
                       default = DEFAULTS['TASK-SET-SIZE-MIN'],
                       help='A lower bound on the number of tasks per '
                       'task set')
    group.add_argument('-Z', '--set-size-ub', type=int,
                       default = DEFAULTS['TASK-SET-SIZE-MAX'],
                       help='An upper bound on the number of tasks per'
                       'task set')

    wcet_desc = 'The WCET c(n) of an object is a function of n ' \
        'threads, it has a BASE and an INCREMENTAL component: ' \
        'c(n) = BASE + (INCREMENTAL * n)'
    
    group = parser.add_argument_group('WCET Arguments', wcet_desc)
    
    group.add_argument('-b', '--base-lb', type=int,
                        default = DEFAULTS['BASE-MIN'],
                        help='A lower bound on all objects base WCET')
    group.add_argument('-B', '--base-ub', type=int,
                        default = DEFAULTS['BASE-MAX'],
                        help='An upper bound on all objects base WCET')
    group.add_argument('-i', '--incremental-lb', type=int,
                        default = DEFAULTS['INCR-MIN'],
                        help='A lower bound on all objects '
                        'incremental WCET as a percentage of the BASE')
    group.add_argument('-I', '--incremental-ub', type=int,
                        default = DEFAULTS['INCR-MAX'],
                        help='An upper bound on all objects '
                        'incremental WCET as a percentage of the BASE')
    return parser
    
# False entry point
def main():
    parser = gen_args()
    cargs = comargs.CommonArgs(parser)
    ctx = colo.RunContext(cargs.namespace)
    
    if cargs.namespace.cfg:
        path = cargs.namespace.cfg
        logging.info(f'Writing to run context file {path}')
        ctx.dumpJSON(path)
    else:
        print(ctx.toJSON())


if __name__ == '__main__':
    main()
