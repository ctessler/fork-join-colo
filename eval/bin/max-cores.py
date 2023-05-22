#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import colo
import comargs
import json
import logging
import os
import pandas
import pathlib

EXACT = ['ExactColo',
          'ExactNoColo' ]
APPROX = [ '3-Parm',
           '3-Parm-HD',
           '2-Gram']
DAG = [ 'DAG-m',
        'DAG-LP',
        'DAG-GB' ]

RESULTS = []
for pfx in EXACT + APPROX + DAG:
    RESULTS.append(pfx + '-Cores')

DESCR='''
Determines the maximum number of cores assigned to any task for
any method
'''

def opt_args():
    parser = argparse.ArgumentParser(
        description=DESCR,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    return parser


def module_start(context_dir):
    '''Entry point when used as a module'''

    ctx_dir = os.path.normpath(context_dir)
    if not os.path.isdir(ctx_dir):
        raise NotADirectoryError(f'{ctx_dir} does not exist')

    task_dir = os.path.normpath(ctx_dir + '/tasks')
    if not os.path.isdir(task_dir):
        raise NotADirectoryError(f'{task_dir} does not exist')
    
    task_files = list(pathlib.Path(task_dir).glob('*.json'))
    count = len(task_files)

    title = 'Loading tasks'
    tasks = []
    with alive_progress.alive_bar(count, title=title) as bar:
        for task_file in task_files:
            with open(task_file, 'r') as fp:
                t = json.load(fp, cls=colo.ForkJoinTaskDecoder)
            tasks.append(t)
            bar()

    maxcores = 0
    for task in alive_progress.alive_it(tasks, title='Parsing Tasks'):
        for result in RESULTS:
            cores = task.get_result(result)
            if not cores:
                continue
            maxcores = max(maxcores, cores)
    print(f'Maximum cores:\n  {maxcores}')

    return 0
    
def main():
    '''Entry point when used a script'''
    parser = opt_args()
    cargs = comargs.CommonArgs(parser)

    return module_start(cargs.namespace.dir)

if __name__ == '__main__':
    exit(main())
