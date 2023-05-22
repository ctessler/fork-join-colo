#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import csv
import re

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
    data = extract(path)
    ires = ins_cycles(data, cpi, brt)

    return ires

def extract(path):
    '''
    Extracts the core access counts
    data = [
        # Core 0
        { 'core'    : core number,
          'daccess' : number of data accesses,
          'dmisses' : number of data misses,
          'iaccess' : number of instruction accesses,
          'imisses' : number of instruction misses
        },
        # Core 1
        { 'core'    : core number,
          'daccess' : number of data accesses,
          'dmisses' : number of data misses,
          'iaccess' : number of instruction accesses,
          'imisses' : number of instruction misses
        },
        ...
        # Core n
        { 'core'    : core number,
          'daccess' : number of data accesses,
          'dmisses' : number of data misses,
          'iaccess' : number of instruction accesses,
          'imisses' : number of instruction misses
        }
    ]
    '''
    data = []
    with open(path) as cachelog:
        tblstart = re.compile(r'^core')
        tblend = re.compile(r'^sum')

        # Get to the first line of the table
        for line in cachelog:
            if tblstart.match(line):
                break

        for line in cachelog:
            if tblend.match(line):
                break
            strs = re.split('\s+', line)
            eles = [int(x) if x.isdigit() else str(x) for x in strs]
            row = { 'core' : eles[0],
                    'daccess' : eles[1],
                    'dmisses' : eles[2],
                    'iaccess' : eles[4],
                    'imisses' : eles[5]
                   }
            data.append(row)

        return data

def ins_cycles(data, cpi, brt):
    '''
    Determines the number of instruction cycles per core

    results = {
        0 : {cycles: number of cycles,
             hits: number of instruction cache hits,
             misses: number of instruction cache misses},
        1 : {cycles: number of cycles,
             hits: number of instruction cache hits,
             misses: number of instruction cache misses},
        .
        .
        n : {cycles: number of cycles,
             hits: number of instruction cache hits,
             misses: number of instruction cache misses}
    }
    '''
    results = {}
    for row in data:
        insn = row['iaccess']
        miss = row['imisses']
        hits = row['iaccess'] - miss
        results[row['core']] = {
            'cycles' : (insn * cpi) + (miss * brt),
            'misses' : miss,
            'hits'   : hits
        }
    return results


def main():
    '''
    Script entry point
    '''
    args = arguments()
    init_logging(args.verbose)
    ires = modstart(args.cachelog, args.cpi, args.brt)

    tcycles = 0;
    thits = 0;
    tmisses = 0;
    print(f'{"core":<6} {"hits":<8} {"misses":<8} {"cycles":<8}')
    for core, data in ires.items():
        cycles = data['cycles']
        hits = data['hits']
        misses = data['misses']

        tcycles += cycles;
        thits += hits
        tmisses += misses

        print(f'{core:<6} {hits:<8} {misses:<8} {cycles:<8}')

    print(f'---------------------------------')
    print(f'{"total":<6} {thits:<8} {tmisses:<8} {tcycles:<8}')
    print(f' * Removing core0 contribution *')
    thits = thits - ires[0]['hits']
    tmisses = tmisses - ires[0]['misses']
    tcycles = tcycles - ires[0]['cycles']
    print(f'{"total":<6} {thits:<8} {tmisses:<8} {tcycles:<8}')


if __name__ == '__main__':
    exit(main())
