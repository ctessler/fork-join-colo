#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import json
import logging
import math
import os
import pathlib
import alive_progress # pip install alive-progress
import random

def serial(sections, base):
    s = (1 + sections) * base
    logging.info(f'Sections:{sections} contribution:{s}')
    return s

def sec_work(threads, base, incr):
    pwork = base + (threads -1) * ((incr / 100) * base)
    logging.info(f'Threads:{threads} base:{base} incr:{incr} parallel contribution:{pwork}')    
    return pwork

def sec_mean_work(work, cores):
    mwork = work / cores
    logging.info(f'Cores:{cores} Avg Parallel contribution:{mwork}')
    return mwork

def avg_total(sections, base, incr, threads, cores):
    s = serial(sections, base)
    w = sec_work(threads, base, incr)
    aw = sec_mean_work(w, cores)

    logging.info(f'Combined:{math.ceil(s + aw)}')
    return math.ceil(s + aw)

def module_start(ctx, cores):
    '''
    Entrypoint when used as a module
    ctx  : the colo.RunContext describing the parameters of the task
    '''

    low = avg_total(ctx.sections[0], ctx.bases[0], ctx.incrs[0],
                    ctx.threads[0], cores)
    
    high = avg_total(ctx.sections[1], ctx.bases[1], ctx.incrs[1],
                    ctx.threads[1], cores)

    print(f'Avg Estimated Workloads: [{low}, {high}]')
    print(f'Recommended Deadlines: [{low * .5}, {low * 1.5}]')
    return

def opt_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-M', '--cores-ub', type=int,
                        default=10,
                        help='An upper bound on the number of cores a'
                        ' task may be allocated')
    return parser
    
def main():
    '''
    Entrypoint for command line invocation
    '''
    parser = opt_args()
    cargs = comargs.CommonArgs(parser)

    if not cargs.namespace.cfg:
        logging.warning('A JSON context file --cfg is required')
        cargs.parser.print_help()
        return

    ctx = colo.RunContext(jsonfile=cargs.namespace.cfg)
    module_start(ctx, cargs.namespace.cores_ub)

if __name__ == '__main__':
    main()
