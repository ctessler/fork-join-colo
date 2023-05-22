#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import json
import logging
import os
import pathlib
import alive_progress # pip install alive-progress

def module_start(context_dir):
    '''Entry point when used as a module'''
    taskdir = os.path.normpath(context_dir + f'/tasks')
    if not os.path.isdir(taskdir):
        raise Exception(f'Task directory: {taskdir} does not exist')

    task_files = list(pathlib.Path(taskdir).glob('*.json'))
    count = len(task_files)

    removed = 0
    logging.info(f'Filtering {count} tasks in {taskdir}')
    with alive_progress.alive_bar(count) as bar:
        for task_file in task_files:
            logging.debug(f'Reading task {task_file}')
            t = None
            with open(task_file, 'r') as fp:
                t = json.load(fp, cls=colo.ForkJoinTaskDecoder)
            bar()
            if t.infeasible():
                logging.debug(f'Task {task_file} is infeasible, removing')
                os.remove(task_file)
                removed += 1
                continue
            if len(t.objects) == 1:
                logging.debug(f'Task {task_file} has one object, removing')
                os.remove(task_file)
                removed += 1
                continue
            demand = t.demand()
            if demand < t.deadline:
                logging.debug(f'Task {task_file} has less demand '
                              f'{demand} than its deadline '
                              f'{t.deadline} (without colocation) '
                              f', removing')
                os.remove(task_file)                
                removed += 1
                continue
    logging.info(f'Removed {removed} tasks from {taskdir}'
                 f', {count - removed} remain')
    
def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs()

    if not cargs.namespace.dir:
        logging.warning('A context directory is required')
        cargs.parser.print_help()
        return

    module_start(cargs.namespace.dir)

if __name__ == '__main__':
    main()
