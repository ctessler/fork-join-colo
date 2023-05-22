#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import json
import logging
import math
import os

from colo.Helpers import Timer

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
    parser.add_argument('task', type=str, action='store',
                        help='Path to the task file being analyzed')
    parser.add_argument('--force',  action='store_true',
                        help='Force recalculation')
    
    return parser


def module_start(task_path, cores_min, cores_max, force=False):
    '''Entry point when used as a module'''
    return colo.Helpers.core_alloc('2-Gram', colo.TwoGram,
                task_path, cores_min, cores_max, force)

    
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
