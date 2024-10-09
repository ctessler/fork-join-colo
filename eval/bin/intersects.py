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
import itertools

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
    print_sched_isects(stats_dir, df, num_tasks)
    print_sched_diffs(stats_dir, df, num_tasks)
    print_approx_diffs(stats_dir, df, num_tasks)

    return 0

def print_sched_isects(graph_dir, df, num_tasks):
    algs = list(df.filter(regex=".*-Sched").columns)
    total = len(df.index)
    combs = []
    for i in range(1, len(algs)+1):
        els = [list(x) for x in itertools.combinations(algs, i)]
        combs.extend(els)

    print(f'Schedulable Tasks | Shared By Algorithms')
    print(f' (pct) (count)    | A isect B isect C ... ')
    print(f'------------------+------------------------')
    for algs in combs:
        rows = df
        for a in algs:
            key = a
            rows = rows[(rows[key] == True)]
        count = len(rows[a].index)
        print(f'{count/total * 100:>6.2f}% {count:<5}     | ', end='')
        print('(' + ' ∩ '.join(shorten(x[:-6]) for x in algs) + ')')
    print(f'------------------+------------------------')
    print(f'100.00% {total:<5}        | Total Tasks (not necessarily schedulable')

def shorten(alg):
    if alg == '3-Parm-HD':
        return '3PHD'

    if alg == '3-Parm':
        return '3P'

    if alg == '2-Gram':
        return '2G'

    if alg == 'DAG-m':
        return 'Dm'

    if alg == 'DAG-GB':
        return 'GB'

    if alg == 'DAG-LP':
        return 'LP'

    return 'UK'

def union(left, right):
    '''Find the union of two pandas.DataFrames (removing duplicates)'''
    result = left.merge(right, 'outer')
    result.drop_duplicates()

    return result

def isect(left, right):
    '''Find the intersection of two pandas.DataFrames'''
    result = left.merge(right, 'inner')
    return result

def subtract(left, right):
    '''Subtracts the right dataframe from the left'''
    i = isect(left, right)
    result = pandas.concat([left, i]).drop_duplicates(keep=False)
    return result

def print_sched_diffs(graph_dir, df, num_tasks):
    df = df.drop(columns=['DAG-m-Sched'])
    algs = list(df.filter(regex=".*-Sched").columns)
    total = len(df.index)
    combs = []
    for i in range(1, len(algs)+1):
        els = [list(x) for x in itertools.combinations(algs, i)]
        combs.extend(els)

    combs = list(itertools.permutations(algs, len(algs)))
    sched = {}
    for a in algs:
        sched[a] = df[df[a] == True]

    for c in combs:
        comb = list(c)

        # comb [ a, b, c, d ... ]
        # The only choice is where to place the intersection
        # a - (b ∪ c ∪ d ...)
        # (a ∩ b) - (c ∪ d ...)
        # (a ∩ b ∩ c) - (d ∪ e ...)
        left = comb.pop()
        lname = shorten(left[:-6])
        for i in range(0, len(comb)):
            # i - index of subtraction
            #     (i-1 the last element of the intersection)
            lname=f'({shorten(left[:-6])}'
            leftframe=sched[left]
            for j in range(0, i):
                lname=f'{lname} ∩ {shorten(comb[j][:-6])}'
                leftframe = isect(leftframe, sched[comb[j]])
            lname=f'{lname})'

            # i - index of the beginning of the union
            rightframe = subtract(leftframe, leftframe)
            for k in range(i, len(comb)):
                for x in comb[k:]:
                    rightframe=union(rightframe, sched[x])
            rname ='(' + ' ∪ '.join(shorten(x[:-6]) for x in comb[i:]) + ')'

            # INTERSECTION - UNION
            result = subtract(leftframe, rightframe)
            count = len(result[left].index)
            print(f'{count:<6} | {lname} - {rname}')
    return

def print_approx_diffs(graph_dir, df, num_tasks):
    df = df.drop(columns=['DAG-m-Sched'])
    df = df.drop(columns=['DAG-LP-Sched'])
    df = df.drop(columns=['DAG-GB-Sched'])
    algs = list(df.filter(regex=".*-Sched").columns)
    total = len(df.index)
    combs = []
    for i in range(1, len(algs)+1):
        els = [list(x) for x in itertools.combinations(algs, i)]
        combs.extend(els)

    combs = list(itertools.permutations(algs, len(algs)))
    sched = {}
    for a in algs:
        sched[a] = df[df[a] == True]

    for c in combs:
        comb = list(c)

        # comb [ a, b, c, d ... ]
        # The only choice is where to place the intersection
        # a - (b ∪ c ∪ d ...)
        # (a ∩ b) - (c ∪ d ...)
        # (a ∩ b ∩ c) - (d ∪ e ...)
        left = comb.pop()
        lname = shorten(left[:-6])
        for i in range(0, len(comb)):
            # i - index of subtraction
            #     (i-1 the last element of the intersection)
            lname=f'({shorten(left[:-6])}'
            leftframe=sched[left]
            for j in range(0, i):
                lname=f'{lname} ∩ {shorten(comb[j][:-6])}'
                leftframe = isect(leftframe, sched[comb[j]])
            lname=f'{lname})'

            # i - index of the beginning of the union
            rightframe = subtract(leftframe, leftframe)
            for k in range(i, len(comb)):
                for x in comb[k:]:
                    rightframe=union(rightframe, sched[x])
            rname ='(' + ' ∪ '.join(shorten(x[:-6]) for x in comb[i:]) + ')'

            # INTERSECTION - UNION
            result = subtract(leftframe, rightframe)
            count = len(result[left].index)
            print(f'{count:<6} | {lname} - {rname}')
    return



def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs()

    return module_start(cargs.namespace.dir,
                        cargs.namespace.skip_exact)

if __name__ == '__main__':
    exit(main())
