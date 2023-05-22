#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import json
import logging
import math
import multiprocessing
import os
import pathlib
import alive_progress # pip install alive-progress
import random

gentasks = __import__('gen-tasks')

def mp_job(q, id, path, objects, ctx):
    task = gentasks.create_task(id, ctx, objects)
    q.put((True, path, task))
    return True

def module_start(path, ctx):
    '''
    Entrypoint when used as a module
    path : the directory which will contain the test
    ctx  : the colo.RunContext describing the parameters of the task
    '''

    objdir = os.path.normpath(path + '/objects')
    if not os.path.isdir(objdir):
        raise Exception(f'Object directory: {objdir} does not exist')

    ntasks = ctx.tasks
    idlen = math.ceil(math.log10(ntasks))

    taskdir = os.path.normpath(path + '/tasks')
    logging.debug(f'Task output directory: {objdir}')
    os.makedirs(taskdir, exist_ok=True)

    objects = []
    for objfile in pathlib.Path(objdir).glob('*.json'):
        with open(objfile, 'r') as fp:
            o = json.load(fp, cls=colo.ForkJoinObjectDecoder)
            objects.append(o)
    # All of the objects are loaded in [objects]

    manager = multiprocessing.Manager()
    evt = manager.Event()
    q = manager.Queue()
    
    # Generate the data
    logging.info(f'Preparing the parallelized data ... ')
    data = []
    for id in alive_progress.alive_it(range(ntasks)):
        idstr = f'{id:0{idlen}}'
        path = os.path.normpath(taskdir + f'/task.{idstr}.json')
        data.append((q, idstr, path, objects, ctx))

    # Generate the tasks
    with multiprocessing.Pool() as pool:
        results = pool.starmap_async(mp_job, data)
        for count in alive_progress.alive_it(range(ntasks)):
            (success, path, task) = q.get()
            logging.debug(f'Writing {task.name} to {path}')
            # write tasks, not parallel safe (for unknown reasons)
            with open(path, 'w') as fp:
                json.dump(task, fp, cls=colo.ForkJoinTaskEncoder,
                          indent=4)

def main():
    '''
    Entrypoint for command line invocation
    '''
    cargs = comargs.CommonArgs()

    if not cargs.namespace.dir:
        logging.warning('A context directory is required')
        cargs.parser.print_help()
        return

    if not cargs.namespace.cfg:
        logging.warning('A JSON context file --cfg is required')
        cargs.parser.print_help()
        return
        
    ctx = colo.RunContext(jsonfile=cargs.namespace.cfg)
    module_start(cargs.namespace.dir, ctx)

if __name__ == '__main__':
    main()
