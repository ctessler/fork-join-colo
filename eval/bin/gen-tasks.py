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

def create_task(id, ctx, objects):
    logging.debug(f'Creating task {id}')
    task = colo.ForkJoinTask(name=id)
    
    # Reset the node idexing
    colo.ForkJoinNode.instance = 0
    
    # Select the number of objects to add to the task
    nobjs = random.randint(*ctx.objs)
    objs = random.sample(objects, nobjs)
    logging.debug(f'Task {id} object count: {nobjs}')
    task.objects = objs

    d = random.randint(*ctx.deadlines)
    task.deadline = d
        
    # Select the number of parallel sections
    secs = random.randint(*ctx.sections)
    names = {}
    for sec in range(secs):
        # Select the number of threads for the section
        threads = random.randint(*ctx.threads)
        # Select |threads| objects for the parallel section
        # each object represents a single thread
        pobjs = random.choices(objs, k=threads)
        pnodes = []
        for obj in pobjs:
            node = colo.ForkJoinNode(object=obj, threads=1)
            if node.name in names:
                raise Exception(f'Node named {name} already exists')
            names[node.name] = True
            pnodes.append(node)
        sec = colo.ParallelSection(pnodes)
        task.add_section(sec)

    # Select the fork and join nodes
    sobjs = random.choices(objs, k=secs + 1)
    for o in sobjs:
        task.add_serial_node(colo.ForkJoinNode(object=o))
    return task
        

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

    logging.info(f'Creating {ntasks} tasks')
    with alive_progress.alive_bar(ntasks) as bar:    
        for i in range(ntasks):
            id = f'{i:0{idlen}}'
            task = create_task(id, ctx, objects)
            tpath = os.path.normpath(taskdir + f'/task.{id}.json')
            with open(tpath, 'w') as fp:
                json.dump(task, fp, cls=colo.ForkJoinTaskEncoder, indent=4)
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
