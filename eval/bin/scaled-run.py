#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import dagot
import json
import logging
import math
import os
import pathlib
import shutil

# Individual components
genobjs = __import__('gen-objects')
gentasks = __import__('gen-tasks')
filtertasks = __import__('filter-tasks')
trimtasks = __import__('trim-tasks-to-bucket')
dispbuckets = __import__('display-buckets')
twogram = __import__('2-gram-par')
threeparmhd = __import__('3-parm-hd-par')
threeparm = __import__('3-parm-par')
exactcolo = __import__('opt-task-colo')
exactnocolo = __import__('opt-task-no-colo')
dagm = __import__('dag-m-par')
daggb = __import__('dag-gb-par')
daglp = __import__('dag-lp-par')
import tabulate
import graph
xsetgraph = __import__('cross-set-graph')
scaletasks = __import__('scale-tasks')

DEFAULTS = {
    'FRAC' : 1/10,
    'BUCKETS' : 10,
    'CORES-MIN' : 1,
    'CORES-MAX' : 5
}

DESCR='''
Creates multiple task sets for evaluation by each of the exact, approximation,
and heuristic algorithms. The task sets share the same structure and
deadlines. They differ in their execution time distribution. One task set is
generated by the given parameters, call this t0.

t1 is produced by augmenting the execution demand of every object's beta and
gamma value by a fraction F of t0. t2 is produced by reducing t0 by double the
fraction.

    t1 = t0 - 1 * (t0 * F)
    t2 = t0 - 2 * (t0 * F)
    ...
    tn = t0 - n * (t0 * F)

By construction n = 1/F

'''

def opt_args():
    parser = argparse.ArgumentParser(
        description=DESCR,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-F', '--fraction', type=float,
                        default=DEFAULTS['FRAC'])
    # parser.add_argument('-U', '--buckets', type=int,
    #                     default=DEFAULTS['BUCKETS'],
    #                     help='the target number of cache reuse intervals')
    parser.add_argument('-m', '--cores-lb', type=int,
                        default=DEFAULTS['CORES-MIN'],
                        help='A lower bound on the number of cores a'
                        ' task may be allocated')
    parser.add_argument('-M', '--cores-ub', type=int,
                        default=DEFAULTS['CORES-MAX'],
                        help='An upper bound on the number of cores a'
                        ' task may be allocated')
    parser.add_argument('-G', '--skip-set-graphs', action='store_true',
                        default=False,
                        help='Prevents the generation of per task set graphs')
    parser.add_argument('-g', '--graphs-only', action='store_true',
                        default=False,
                        help='Regenerates the graphs (only)')
    
    return parser

IDLEN=1
def tset_name(frac):
    name = f'{frac:0.2f}Y'
    return name

def tset_path(ctxdir, frac):
    name = tset_name(frac)
    path = os.path.normpath(ctxdir + f'/{name}')
    return path

def tset_copy(pathzero, newpath):
    if pathzero == newpath:
        # Nothing to do
        return
    shutil.copytree(pathzero, newpath)

def gen_tset_paths(ctxdir, frac, iterations):
    '''Generates the task set paths in decreasing weight order
    If F = .1, then return value is [1.0Y, .9Y, .8Y, ..., .1Y]
    '''
    tset_paths = []
    for i in range(iterations):
        q = 1 - (frac * i)
        path = tset_path(ctxdir, q)
        tset_paths.append(path)
    return tset_paths

def gen_tset_names(ctxdir, frac, iterations):
    '''Generates the task set names in decreasing weight order
    If F = .1, then return value is [1.0Y, .9Y, .8Y, ..., .1Y]
    '''
    tset_names = []
    for i in range(iterations):
        q = 1 - (frac * i)
        name = tset_name(q)
        tset_names.append(name)
    return tset_names

def gen_tset_fracs(frac, iterations):
    fracs = []
    for i in range(iterations):
        q = 1 - (frac * i)
        fracs.append(q)
    return fracs

def tset_seed(ctx, path):
    '''Creates the seed set of tasks'''
    # Task set name

    logging.info(f'Generating objects')
    genobjs.module_start(path, ctx)

    logging.info(f'Generating tasks')
    gentasks.module_start(path, ctx)


def tset_copy_scale(paths, fracs, buckets):
    '''Copies the seed task to new task sets and scales them according to
    fracs'''

    trimandbucket = False
    # Trimming and bucketing violates the purpose of scaling tasks 
    
    # Copy the seed to new task sets and scale them
    for (q, path) in zip(fracs[1:], paths[1:]):
        logging.info(f'Copying {paths[0]} to {path}')
        tset_copy(paths[0], path)

        logging.info(f'Scaling task set {path} by {q}')
        scaletasks.module_start({'incr-q' : q}, path)

        if trimandbucket:
            logging.info(f'Filtering task set {path}')
            filtertasks.module_start(path)

            logging.info(f'Trimming task set {paths[0]} to {buckets} buckets')
            trimtasks.module_start(paths[0], buckets)
        
        logging.info(f'Displaying buckets for {path}')        
        dispbuckets.module_start(path)

    if trimandbucket:
        # Don't forget the seeding task
        logging.info(f'Filtering task set {paths[0]}')
        filtertasks.module_start(paths[0])

        logging.info(f'Trimming task set {paths[0]} to {buckets} buckets')
        trimtasks.module_start(paths[0], buckets)

    logging.info(f'Displaying buckets for {paths[0]}')
    dispbuckets.module_start(paths[0])

        

def tset_run_algs(paths, cores_min, cores_max, skip_exact, skip_dag):
    '''Runs each of the schedulability tests'''
    for path in paths:
        logging.info(f'Creating task set {path}')

        twogram.module_start(path, cores_min, cores_max)
        threeparmhd.module_start(path, cores_min, cores_max)
        threeparm.module_start(path, cores_min, cores_max)

        if skip_exact:
            logging.info('Skipping exact algorithms')
        else:
            taskdir = os.path.normpath(path + '/tasks')
            files = list(pathlib.Path(taskdir).glob('*.json'))
            for task in files:
                exactcolo.module_start(task, cores_min, cores_max)
                exactnocolo.module_start(task, cores_min, cores_max)

        if skip_dag:
            logging.info('Skipping DAG algorithms')
        else:
            dagm.module_start(path, cores_min, cores_max)
            daggb.module_start(path, cores_min, cores_max)
            daglp.module_start(path, cores_min, cores_max)
    

def module_start(ctxfile, ctxdir, frac, buckets,
                 skip_exact, skip_dag, skip_set_graphs, graphs_only,
                 cores_min, cores_max):
    '''Entry point when used as a module
    ctxfile - path to the context file describing the task set parameters
    ctxdir  - the directory that will contain the results
    frac    - the fraction by which to modify task sets
    '''
    ctx = colo.RunContext(jsonfile=ctxfile)
    iterations = math.ceil(1/frac)
    IDLEN = int(math.log10(iterations))
    logging.info(f'Context:{ctxfile} directory:{ctxdir} fraction:{frac} '
                 f'iterations:{iterations}')
    logging.info(f'  skip exact:{skip_exact} skip dag:{skip_dag}')

    tset_paths = gen_tset_paths(ctxdir, frac, iterations)
    tset_names = gen_tset_names(ctxdir, frac, iterations)
    fracs = gen_tset_fracs(frac, iterations)

    # Create the seed task set
    if graphs_only:
        logging.info('Skipping task set generation, only graphing')
    else:
        logging.info(f'Creating task set {tset_paths[0]}')
        tset_seed(ctx, tset_paths[0])

        # Copy the seed to new task sets and scale
        tset_copy_scale(tset_paths, fracs, buckets)

    if graphs_only:
        logging.info('Skipping algorithm invocations, only graphing')
    else:
        # Run the algorithms
        tset_run_algs(tset_paths, cores_min, cores_max, skip_exact, skip_dag)

    # Tabulate the data and generate the per set graphs
    for path in tset_paths:
        # Tabulate the data (per set)
        logging.info(f'Tabulating {path} skip_exact:{skip_exact}')
        tabulate.module_start(path, skip_exact)

        # Graphing the data (per set)
        if skip_set_graphs:
            logging.info(f'Skipping individual graphs for {path}')
        else:
            logging.info(f'Generating the individual graphs for {path}')
            graph.module_start(path, skip_exact)

    # Generate the comprehensive graphs
    if len(tset_paths) < 2:
        logging.info(f'Fewer than 2 task sets, skipping cross set graphs')
    else:
        graph_path = os.path.normpath(ctxdir + '/graphs')
        os.makedirs(graph_path, exist_ok=True)
        xsetgraph.module_start(graph_path, tset_paths, tset_names, skip_exact)
        
    return 0
    
def main():
    '''Entry point when used a script'''
    parser = opt_args()
    cargs = comargs.CommonArgs(parser)

    if not cargs.namespace.dir:
        logging.warning('A context directory is required')
        cargs.parser.print_help()
        return

    if not cargs.namespace.cfg:
        logging.warning('A JSON context file --cfg is required')
        cargs.parser.print_help()
        return

    return module_start(cargs.namespace.cfg,
                        cargs.namespace.dir,
                        cargs.namespace.fraction,
                        0,
#                        cargs.namespace.buckets,
                        cargs.namespace.skip_exact,
                        cargs.namespace.skip_dag,
                        cargs.namespace.skip_set_graphs,
                        cargs.namespace.graphs_only,
                        cargs.namespace.cores_lb,
                        cargs.namespace.cores_ub)

if __name__ == '__main__':
    exit(main())
