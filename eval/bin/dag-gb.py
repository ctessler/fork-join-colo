#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import dagot
import json
import logging
import os

from colo.Helpers import Timer
from dagot.GreatestBenefit import greatest_benefit

DEFAULTS = {
    # Minimum number of cores to allocated to a task
    'CORES-MIN' : 1,
    'CORES-MAX' : 10
}

DESCR='''
The calculation of minimum number of cores per task using the Greatest
Benefit heuristic. Designed for general DAG tasks, this is the basis
of the DAG-OT work. 
'''

def opt_args():
    parser = argparse.ArgumentParser(
        description=DESCR,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-m', '--cores-lb', type=int,
                        default=DEFAULTS['CORES-MIN'],
                        help='A lower bound on the number of cores a'
                        ' task may be allocated')
    parser.add_argument('-M', '--cores-ub', type=int,
                        default=DEFAULTS['CORES-MAX'],
                        help='An upper bound on the number of cores a'
                        ' task may be allocated')
    parser.add_argument('task', type=str, action='store',
                        help='Path to the task file being analyzed')
    parser.add_argument('--force',  action='store_true',
                        help='Force recalculation')
    
    return parser

def results(task, cores_min, cores_max):
    pfx='DAG-GB'
    timer = Timer()
    cores = 0

    timer.start()
    cores = greatest_benefit(task)
    timer.stop()

    result = {
        f'{pfx}-Cores'      : cores,
        f'{pfx}-Terminated' : False,
        f'{pfx}-WCET'       : 0,
        f'{pfx}-Seconds'    : timer.elapsed
    }
    return result


def module_start(task_path, cores_min, cores_max, force=False):
    '''Entry point when used as a module'''
    pfx='DAG-GB'

    path = os.path.normpath(task_path)
    if not os.path.isfile(path):
        raise Exception(f'Task file: {path} does not exist')

    with open(path, 'r') as fp:
        task_read = json.load(fp, cls=colo.ForkJoinTaskDecoder)
        fp.seek(0, 0)
        task_write = json.load(fp, cls=colo.ForkJoinTaskDecoder)        
        

    # the task that was read in earlier has been modified
    # writing it back to disk would be a problem.
    res = results(task_read, cores_min, cores_max)

    for key, value in res.items():
        task_write.set_result(key, value)

    with open(path, 'w') as fp:
        json.dump(task_write, fp, cls=colo.ForkJoinTaskEncoder, indent=4)
    
    return 0
    
def main():
    '''Entry point when used a script'''
    parser = opt_args()
    cargs = comargs.CommonArgs(parser)

    return module_start(cargs.namespace.task, 
                        cargs.namespace.cores_lb,
                        cargs.namespace.cores_ub,
                        cargs.namespace.force)

if __name__ == '__main__':
    exit(main())
