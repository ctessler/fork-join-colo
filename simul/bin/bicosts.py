#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import csv
import re
import cycles

DFLT = {
    'cpi' : 1,
    'brt' : 2048
}

def arguments():
    '''
    Parses the arguments from the command line

    returns an argparse.ArgumentParser.parse_args() object
    '''
    fclass = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=fclass)

    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Increase the logging level')
    parser.add_argument('-c', '--cpi', type=int, default=DFLT['cpi'],
                        help='Constant for cycles per instruction')
    parser.add_argument('-b', '--brt', type=int, default=DFLT['brt'],
                        help='Constant for block reload time')
    parser.add_argument('cachelog', type=str, action='store',
                        help='Path to the cache.log being analyzed')

    parsed = parser.parse_args()
    return parsed

def init_logging(verbosity):
    '''
    Initializes the logging module
    '''
    level = verbosity * -10 + logging.INFO
    logargs = {
        'format'  : "%(asctime)s [%(levelname)s] > %(message)s",
        'datefmt' : "%H:%M:%S",
        'level'   : level
    }

    logging.basicConfig(**logargs)
    logging.debug(f'Debug logging enable')


def modstart(path, cpi, brt):
    '''
    Module entry point
    path - path to the cache.log file
    cpi  - constant for cycles per instruction
    brt  - constant for block reload time

    returns the instruction results
    '''
    ires = cycles.modstart(path, cpi, brt)

    costs = []
    cores = sorted(ires.keys())
    cores.pop(0)
    it = iter(cores)
    for core in it:
        try:
            idx = next(it)
            b   = ires[core]['cycles']
            bi  = ires[idx]['cycles']
            row = {'base' : b,
                   'incr' : bi - b,
                   'incrf' : (bi - b)/ b }
            costs.append(row)
        except:
            break

    return costs

def main():
    '''
    Script entry point

    Calculates the base and incremental costs for the MRTC benchmarks,
    this ASSUMES the fork-join task structure of the fj-g* sample
    directories.
    '''
    args = arguments()
    init_logging(args.verbose)
    costs = modstart(args.cachelog, args.cpi, args.brt)

    for cost in range(len(costs)):
        base = costs[cost]['base']
        incr = costs[cost]['incr']
        incp = incr / base
        print(f'object:{cost + 1:<2} base:{base:<10} incr:{incr:<10}'
              f' ipct:{incp:<10.2}')


if __name__ == '__main__':
    exit(main())
