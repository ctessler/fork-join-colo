#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import comargs
import colo
import json
import logging
import numpy
import os
import pandas
import pathlib
import sys
import graph

EXACT = ['ExactColo',
          'ExactNoColo' ]
APPROX = [ '3-Parm',
           '3-Parm-HD',
           '2-Gram']
DAG = [ 'DAG-m',
        'DAG-LP',
        'DAG-GB' ]
PFX = []
TASK_RESULTS = []
    
def append_sched(df):
    '''
    Appends the schedulability information for each algorithm to
    each row of the dataframe
    '''
    max_core = 0
    for pfx in APPROX + EXACT:
        sched = f'{pfx}-Sched'
        wcet  = f'{pfx}-WCET'
        cores = f'{pfx}-Cores'
        if not wcet in df.columns:
            continue
        df[sched] = df.apply(
            lambda row: row['Deadline'] >= row[wcet], axis=1)
        max_core = max(max_core, df[cores].max())

    for pfx in DAG:
        sched = f'{pfx}-Sched'
        cores = f'{pfx}-Cores'
        df[sched] = df.apply(
            lambda row: row[cores] > 0 and row[cores] <= max_core, axis=1)

def module_start(context_dir, skip_exact=False):
    '''
    Entry point when used as a module

    context_dir - the directory containing the results after they have
                  been processed by the WCET and scheduling algorithms 
    '''
    TASK_RESULTS = []
    PFX = []
    for pfx in APPROX + DAG:
        TASK_RESULTS.append(pfx + '-Cores')
        TASK_RESULTS.append(pfx + '-WCET')
        TASK_RESULTS.append(pfx + '-Seconds')
        TASK_RESULTS.append(pfx + '-Terminated')
        PFX.append(pfx)
    if not skip_exact:
        for pfx in EXACT:
            TASK_RESULTS.append(pfx + '-Cores')
            TASK_RESULTS.append(pfx + '-WCET')
            TASK_RESULTS.append(pfx + '-Seconds')
            TASK_RESULTS.append(pfx + '-Terminated')
            PFX.append(pfx)
    
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

    tdata = []
    doexact = True
    for task in alive_progress.alive_it(tasks, title='Parsing Tasks'):
        row = [task.name, task.deadline,
               task.cache_reuse_factor(), task.total_threads()]
        for result in TASK_RESULTS:
            res = task.get_result(result)
            if res == None:
                res = sys.maxsize
            if not result:
                raise Warning(f'{task} has no result for {result}'
                              ' skipping.')
            row.append(res)
        tdata.append(row)

    task_csv = os.path.normpath(ctx_dir + '/tasks.csv')
    with alive_progress.alive_bar(1, title=f'{task_csv}')  as bar:
        cols = [ 'Name', 'Deadline', 'CacheReuseFactor',
                 'TotalThreads', *TASK_RESULTS]
        dataframe = pandas.DataFrame(tdata, columns=cols)
        dataframe.set_index(['Name'], inplace=True)
        append_sched(dataframe)
        dataframe.to_csv(task_csv)
        bar()
        
    return 0

def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs()

    return module_start(cargs.namespace.dir,
                        cargs.namespace.skip_exact)

if __name__ == '__main__':
    exit(main())
