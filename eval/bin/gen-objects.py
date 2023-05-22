#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import comargs
import colo
import json
import logging
import math
import os
import random

def module_start(path, ctx):
    '''
    Entrypoint when used as a module
    path : the directory which will contain the objects
    ctx  : the colo.RunContext describing the parameters of the task
    '''
    num_objs = ctx.objs[1]
    logging.debug(f'Number of objects {num_objs}')

    idlen = math.ceil(math.log10(num_objs))

    objdir = os.path.normpath(path + '/objects')
    logging.debug(f'Object output directory: {objdir}')
    os.makedirs(objdir, exist_ok=True)

    for i in range(num_objs):
        id = f'{i:0{idlen}}'
        # For each object generate a WCET function given the base
        # and incremental thread values in the range
        base = random.randint(*ctx.bases)
        logging.debug(f'Object {id} base: {base} in {ctx.bases}')

        # Treating the increment values as a percentage range
        incr_pct = random.randint(ctx.incrs[0], ctx.incrs[1]) / 100
        incr = math.floor(base * incr_pct)
        logging.debug(f'Object {id} incr: {incr} in '
                      f'[{ctx.incrs[0]}, {base}]')
        o = colo.ForkJoinObject(f'{id}', colo.WCET(base, incr))
        opath = os.path.normpath(objdir + f'/object.{id}.json')
        with open(opath, 'w') as fp:
            json.dump(o, fp, cls=colo.ForkJoinObjectEncoder, indent=4)

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

    print(cargs.namespace.cfg)
    ctx = colo.RunContext(jsonfile=cargs.namespace.cfg)
    module_start(cargs.namespace.dir, ctx)

if __name__ == '__main__':
    main()
