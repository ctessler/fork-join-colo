#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import comargs
import colo
import json
import logging
import math
import os
import pathlib
import sys

DFLT = {
    'incr-q' : 0.5
}

def opt_args():
    '''
    Optional arguments specific to task scaling
    '''
    DESCR='''
    Scales every task's parameters by a constant, no other task
    features (or structure) is modified.
    '''

    
    parser = argparse.ArgumentParser(
        description=DESCR,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument_group(title='scale-tasks.py arguments')
    qhelp="Quotient to apply to all task's incremental cost (0, 1]"
    parser.add_argument('-q', '--incremental-quotient', type=float,
                        default=DFLT['incr-q'], help=qhelp)

    return parser

def debug_str(obj):
    str = f'obj:{obj.name} base:{obj.wcet_fn.base} incr:{obj.wcet_fn.incr} '
    str += f'o(1):{obj.wcet_fn(1)} o(2):{obj.wcet_fn(2)}'

    return str

def module_start(factors, context_dir, skip_exact=False):
    '''
    Entry point when used as a module

    context_dir - the directory containing the results after they have
                  been processed by the WCET and scheduling algorithms 
    '''
    ctx_dir = os.path.normpath(context_dir)
    if not os.path.isdir(ctx_dir):
        raise NotADirectoryError(f'{ctx_dir} does not exist')

    task_dir = os.path.normpath(ctx_dir + '/tasks')
    if not os.path.isdir(task_dir):
        raise NotADirectoryError(f'{task_dir} does not exist')
    
    task_files = list(pathlib.Path(task_dir).glob('*.json'))
    count = len(task_files)

    for key, value in factors.items():
        logging.debug(f'Factor {key}:{value}')

    tasks = []
    title = 'Loading tasks'
    for task_file in alive_progress.alive_it(task_files, title=title):
        with open(task_file, 'r') as fp:
            t = json.load(fp, cls=colo.ForkJoinTaskDecoder)
        tasks.append(t)

    factor = factors['incr-q']
    title = f"Scaling all task's incremental by {factor}"
    for task in alive_progress.alive_it(tasks, title=title):
        tname = task.name
        for obj in task.objects:
            logging.debug('pre : ' + debug_str(obj))
            post = math.ceil(obj.wcet_fn.incr * factor)
            obj.wcet_fn.incr = post
            logging.debug('post: ' + debug_str(obj))

    title = f'Writing tasks'
    for task in alive_progress.alive_it(tasks, title=title):
        path = os.path.normpath(task_dir + f'/task.{task.name}.json')
        with open(path, 'w') as fp:
            json.dump(task, fp, cls=colo.ForkJoinTaskEncoder,
                      indent=4)
        
    return 0

def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs(opt_args())

    factors = {
        'incr-q' : cargs.namespace.incremental_quotient
    }

    return module_start(factors,
                        cargs.namespace.dir,
                        cargs.namespace.skip_exact)

if __name__ == '__main__':
    exit(main())
