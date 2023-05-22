#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import alive_progress # pip install alive-progress
import argparse
import comargs
import colo
import json
import logging
import os
import pathlib

import multiprocessing
import multiprocessing.dummy

daggb = __import__('dag-gb')

DEFAULTS = {
    # Minimum number of cores to allocated to a task
    'CORES-MIN' : 1,
    'CORES-MAX' : 10
}

DESCR='''
The calculation of minimum number of cores per task using the Greatest
Benefit heuristic for multiple tasks calculated using parallel
processes. The heuristic is designed for general DAG tasks.
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
    parser.add_argument('--force',  action='store_true',
                        help='Force recalculation')
    
    return parser

def mp_job(q, task_path, task, cores_min, cores_max, force):
    try:
        results = daggb.results(task, cores_min, cores_max)
        rval = (True, task_path, results, None)
        success = True
    except Exception as e:
        rval = (False, task_path, {}, str(e))
        success = False
    q.put(rval)
    return success

def module_start(path, cores_min, cores_max, force=False):
    '''Entry point when used as a module'''
    path = os.path.normpath(path + '/tasks')
    if not os.path.isdir(path):
        raise Exception(f'Task directory {path} does not exist')

    task_files = list(pathlib.Path(path).glob('*.json'))
    count = len(task_files)

    manager = multiprocessing.Manager()
    evt = manager.Event()
    q = manager.Queue(1024)

    data = []
    logging.info(f'Reading {count} files ...')
    with alive_progress.alive_bar(count) as bar:
        for task_path in task_files:
            with open(task_path, 'r') as fp:
                try:
                    task = json.load(fp, cls=colo.ForkJoinTaskDecoder)
                except Exception as e:
                    msg=f'{task_path} failed to be read, aborting\n'
                    logging.warning(msg + str(e))
                    exit(-1)
                data.append((q, task_path, task, cores_min, cores_max, force))
            bar()

    # data is task files
    logging.info('Calculating minimum cores via (G)reatest (B)enefit')
    with multiprocessing.Pool() as pool:
        results = pool.starmap_async(mp_job, data)
        with alive_progress.alive_bar(count) as bar:
            for c in range(count):
                (success, path, results, error) = q.get()
                logging.debug(f'{path} success {success}')
                if not success:
                    logging.error(f'{path} failed, aborting\n{error}')
                    raise Exception(f'{path} failed.')
                with open(path, 'r') as fp:
                    task = json.load(fp, cls=colo.ForkJoinTaskDecoder)
                    for key, value in results.items():
                        task.set_result(key, value)
                with open(path, 'w') as fp:
                    json.dump(task, fp, cls=colo.ForkJoinTaskEncoder,
                              indent=4)
                bar()
    return 0

    
def main():
    '''Entry point when used a script'''
    parser = opt_args()
    cargs = comargs.CommonArgs(parser)

    if not cargs.namespace.dir:
        logging.warning('A context directory is required')
        cargs.parser.print_help()
        return

    return module_start(cargs.namespace.dir,
                        cargs.namespace.cores_lb,
                        cargs.namespace.cores_ub,
                        cargs.namespace.force)

if __name__ == '__main__':
    exit(main())
