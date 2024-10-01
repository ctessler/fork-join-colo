#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import comargs
import colo
import json
import logging
import math
import matplotlib.pyplot as plt
import numpy
import os
import pandas
import pathlib

EXACT = ['ExactColo',
         'ExactNoColo' ]
APPROX = [ '3-Parm',
           '3-Parm-HD',
           '2-Gram']
DESC = {
    'ExactColo' : 'Exact Minimim With Co-Location',
    'ExactNoColo' : 'Exact Minimum Without Co-Location',
    '3-Parm' : '3-Factor Approximation',
    '3-Parm-HD' : '3-Factor Approximation with Heuristic Deadline',
    '2-Gram' : '2-Factor Approximation (Gram)'
}

LABELS = {
    'ExactColo': 'Exact Colo',
    'ExactNoColo' : 'Exact No Colo',
    '3-Parm' : '3-Parm',
    '3-Parm-HD' : '3-Parm-HD',
    '2-Gram' : 'Gram'
}


PFX = []
MARKER = {}
TASK_RESULTS = []

def module_start(context_dir, skip_exact=False):
    '''
    Entry point when used as a module

    context_dir - the directory containing the results after they have
                  been processed by the WCET and scheduling algorithms
    '''
    for pfx in APPROX:
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

    task_csv = os.path.normpath(ctx_dir + '/tasks.csv')
    if not os.path.isfile(task_csv):
        raise FileNotFoundError(f'{task_csv} does not exist')

    stats_dir = os.path.normpath(ctx_dir + '/stats')
    os.makedirs(stats_dir, exist_ok=True)

    df = pandas.read_csv(task_csv)
    df.set_index('Name', inplace=True)

    num_tasks = len(df.index)
    print_avg_core_alloc(stats_dir, df, num_tasks)

    avg_reuse = df['CacheReuseFactor'].mean()
    print(f'Avg. Cache Reuse Factor = {avg_reuse:.2f}')

    return 0

def print_avg_core_alloc(graph_dir, df, num_tasks):
    print(f'            Over All Tasks')
    print(f'Method      | # Sched. Tasks (%) | Mean Cores ')
    print(f'----------------------------------------')
    algs = list(df.filter(regex=".*-Cores").columns)
    for alg in algs:
            sched_key = alg[:-6] + "-Sched"
            sched = df[(df[sched_key] == True)]
            count = len(sched[alg].index)
            pct = 100 * (count / num_tasks)
            print(f'{alg[:-6]:11} | {count:>10} ({pct:>5.2f}) | {sched[alg].mean():.2f}')
    print(f'----------------------------------------')
    print(f'|Tasks|     = {len(df.index):14}')

def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs()

    return module_start(cargs.namespace.dir,
                        cargs.namespace.skip_exact)

if __name__ == '__main__':
    exit(main())
