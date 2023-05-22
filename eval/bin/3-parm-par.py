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
three_parm = __import__('3-parm')

DEFAULTS = {
    # Minimum number of cores to allocated to a task
    'CORES-MIN' : 1,
    'CORES-MAX' : 10
    
}

def opt_args():
    parser = argparse.ArgumentParser(
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


def module_start(path, cores_min, cores_max, force=False):
    '''Entry point when used as a module'''
    path = os.path.normpath(path + '/tasks')
    if not os.path.isdir(path):
        raise Exception(f'Task directory {path} does not exist')

    task_files = list(pathlib.Path(path).glob('*.json'))
    count = len(task_files)

    with alive_progress.alive_bar(count) as bar:
        for task_file in task_files:
            three_parm.module_start(task_file, cores_min, cores_max,
                                    force)
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
