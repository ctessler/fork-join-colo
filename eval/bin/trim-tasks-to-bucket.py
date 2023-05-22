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
import shutil

DEFAULTS={
    'TASK-LIMIT' : 10
}
def module_start(context_dir, task_limit):
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

    trimmed_tasks = []
    for i in range(len(bins) - 1):
        subf = df[(df[fkey] > bins[i]) &
                  (df[fkey] <= bins[i + 1])]
        saved = subf['Name'].tolist()
        saved = saved[:task_limit]
        for name in saved:
            trimmed_tasks.append(tasks[name])


    bucketdir = os.path.normpath(ctx_dir + '/bucketed')
    shutil.rmtree(bucketdir, ignore_errors=True)
    os.makedirs(bucketdir, exist_ok=True)

    idlen = math.ceil(math.log10(len(tasks.values())))
    ntasks = len(trimmed_tasks)
    logging.info(f'Writing tasks to bucket directory {ntasks} tasks')
    with alive_progress.alive_bar(ntasks) as bar:
        for task in trimmed_tasks:
            id = f'{task.name:0{idlen}}'
            tpath = os.path.normpath(bucketdir + f'/task.{id}.json')
            with open(tpath, 'w') as fp:
                json.dump(task, fp, cls=colo.ForkJoinTaskEncoder, indent=4)
            bar()

    archivedir = os.path.normpath(ctx_dir + '/all-tasks')
    shutil.rmtree(archivedir, ignore_errors=True)
    shutil.move(task_dir, archivedir)
    shutil.move(bucketdir, task_dir)
    return 0

def gen_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-U', '--limit', type=int,
                        default=DEFAULTS['TASK-LIMIT'],
                        help='The target number of tasks per interval')
    return parser

def main():
    '''Entry point when used a script'''
    parser = gen_args()
    cargs = comargs.CommonArgs(parser)

    return module_start(cargs.namespace.dir,
                        cargs.namespace.limit)

if __name__ == '__main__':
    exit(main())
