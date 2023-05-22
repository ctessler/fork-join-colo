#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import comargs
import colo
import json
import logging
import math
import numpy
import os
import pandas
import pathlib

DEFAULTS={
    'TASK-LIMIT' : 10
}

SECS = [
    '3-Parm-Seconds',
    '3-Parm-HD-Seconds',
    '2-Gram-Seconds',
    'ExactNoColo-Seconds',
    'ExactColo-Seconds'
    ]

MAX_SECS = {}
for s in SECS:
    MAX_SECS[s] = 0

def module_start(context_dir):
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

    title = 'Loading tasks'
    tasks = {}
    with alive_progress.alive_bar(count, title=title) as bar:
        for task_file in task_files:
            with open(task_file, 'r') as fp:
                t = json.load(fp, cls=colo.ForkJoinTaskDecoder)
            tasks[t.name] = t
            bar()

    tdata = []
    for task in alive_progress.alive_it(tasks.values(), title='Parsing Tasks'):
        row = [task.name, task.cache_reuse_factor()]
        for s in SECS:
            elapsed = task.get_result(s)
            if (elapsed != None) and (elapsed > MAX_SECS[s]):
                MAX_SECS[s] = elapsed
        tdata.append(row)

    fkey = 'AvgCacheReuseFactor'
    dataframe = pandas.DataFrame(tdata, columns=['Name', fkey])
    df = dataframe
    sf, bins = pandas.cut(df[fkey], bins=10, retbins=True)
    subf = df[fkey].value_counts(bins=bins, sort=False)

    print(f"{'Interval':<20} : Count")
    print(f"----------------------------")
    for i in subf.index:
        print(f'{str(i):<20} : ' + str(subf[i]))

    # Timing information
    print(f'\nWorst Case Times')
    print(f"----------------------------")
    for key, value in MAX_SECS.items():
        print(f'{key:<20}: {value:0.2f}')
        

    return 0

def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs()

    return module_start(cargs.namespace.dir)


if __name__ == '__main__':
    exit(main())
