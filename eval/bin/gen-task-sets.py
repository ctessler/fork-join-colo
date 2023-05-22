#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import alive_progress # pip install alive-progress
import argparse
import comargs
import colo
import json
import logging
import math
import os
import pathlib
import random

def create_task_set(id, ctx, task_list):
    logging.debug(f'Creating taskset {id}')
    
    # Reset the node idexing
    colo.ForkJoinNode.instance = 0
    
    # Select the number of tasks to the task set
    ntasks = random.randint(*ctx.set_sizes)
    logging.debug(f'Task:{id} number of tasks {ntasks}')
    tasks = random.sample(task_list, ntasks)
    logging.debug(f'Task {id} task count: {ntasks}')

    taskset = colo.ForkJoinTaskSet(id)
    taskset.tasks = tasks

    return taskset
        

def module_start(path, ctx):
    '''
    Entrypoint when used as a module
    path : the directory which will contain the test
    ctx  : the colo.RunContext describing the parameters of the task
    '''

    taskdir = os.path.normpath(path + '/tasks')
    if not os.path.isdir(taskdir):
        raise Exception(f'Task directory: {taskdir} does not exist')

    setdir = os.path.normpath(path + '/tasksets')
    logging.info(f'Taskset output directory: {setdir}')
    os.makedirs(setdir, exist_ok=True)

    globs = pathlib.Path(taskdir).glob('*.json')
    task_files = list(globs)
    count = len(task_files)
    tasks = []

    logging.info(f'Reading {count} Task Files')
    with alive_progress.alive_bar(count) as bar:        
        for taskfile in task_files:
            with open(taskfile, 'r') as fp:
                t = json.load(fp, cls=colo.ForkJoinTaskDecoder)
                tasks.append(t)
            bar()
    # All of the tasks are loaded in [tasks]

    nsets = ctx.tasksets
    idlen = math.ceil(math.log10(nsets))
    logging.info(f'Generating {nsets} Task Sets')
    with alive_progress.alive_bar(nsets) as bar:    
        for i in range(nsets):
            id = f'{i:0{idlen}}'        
            taskset = create_task_set(id, ctx, tasks)
            setpath = os.path.normpath(setdir + f'/taskset.{id}.json')
            with open(setpath, 'w') as fp:
                json.dump(taskset, fp, cls=colo.ForkJoinTaskSetEncoder,
                          indent=4)
            bar()

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
