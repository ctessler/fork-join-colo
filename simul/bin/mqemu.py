#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import cycles as modcycles
import logging
import numpy
import os
import subprocess


DFLT = {
    'cpi' : 1,
    'brt' : 2048,
    'iter' : 100,
    'pfx'  : '',
    'qemu' : os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'qemu.sh')
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
    parser.add_argument('-f', '--pfx', type=str,
                        default=DFLT['pfx'], help='Algorithm prefix')
    parser.add_argument('-i', '--iters', type=int, default=DFLT['iter'],
                        help='The number of iterations to execute the image')
    parser.add_argument('-q', '--qemu', type=str, default=DFLT['qemu'],
                        help='Path to command to run qemu, must output cache.log')
    parser.add_argument('--interactive', action='store_true', default=False,
                        help='Use interactive mode')
    parser.add_argument('image', type=str, action='store',
                        help='Path to the riscv32 image being run')

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


def modstart(image, qemu, cpi, brt, iters, interactive=False):
    '''
    Module entry point
    image - path to the image
    qemu  - path to qemu script
    cpi   - constant for cycles per instruction
    brt   - constant for block reload time

    returns the instruction results
    '''

    cycles = []
    longs = []
    misses = []

    for i in range(iters):
        logging.debug(f'{i+1:>3}: Running ... ')
        subprocess.call(['sh', qemu, image],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
        logging.debug(f'{i+1:>3}: Done! ')
        ires = modcycles.modstart('cache.log', cpi, brt)
        if interactive:
            s = input('Accept? [Yn]: ')
            if s.casefold() == 'n':
                logging.debug('Rejected!')
                continue

        sub_cycles = 0
        sub_longs = 0
        sub_misses = 0
        for key,data in ires.items():
            if key == 0:
                # Don't include core 0
                continue
            sub_cycles += data['cycles']
            if data['cycles'] > sub_longs:
                sub_longs = data['cycles']
            sub_misses += data['misses']

        cycles.append(sub_cycles)
        longs.append(sub_longs)
        misses.append(sub_misses)

    cycles = [numpy.array(cycles)]
    longs = [numpy.array(longs)]
    misses = [numpy.array(misses)]

    result = {
        'cycles'  : [numpy.mean(cycles), numpy.std(cycles)],
        'longest' : [numpy.max(longs), numpy.std(longs)],
        'misses'  : [numpy.mean(misses), numpy.std(misses)]
    }

    return result

def main():
    '''
    Script entry point

    Calculates the base and incremental costs for the MRTC benchmarks,
    this ASSUMES the fork-join task structure of the fj-g* sample
    directories.
    '''
    args = arguments()
    init_logging(args.verbose)
    res = modstart(args.image, args.qemu, args.cpi, args.brt,
                   args.iters, args.interactive)

    tc, tcstd = res['cycles']
    l, lstd   = res['longest']
    m, mstd   = res['misses']

    print(f'Average Total Cycles: {tc:<12,.2f}')
    print(f'Std Dev Total Cycles: {tcstd:<5,.2f}')
    print(f'Average Cache Misses: {m:<12,.2f}')
    print(f'Std Dev Cache Misses: {mstd:<5,.2f}')
    print(f'Max Single Sched    : {l:<12,.2f}')
    print(f'Std Dev Single Sched: {lstd:<12,.2f}')

    pfx=args.pfx

    csvpath='data.csv'
    header=[f'Alg.',
            f'Total.Cycles.Avg',
            f'Total.Cycles.SDev',
            f'Misses.Avg',
            f'Misses.SDev',
            f'Longest.Schd',
            f'Longest.SDev']

    with open(csvpath, 'w') as csvfile:
        write = csv.writer(csvfile)
        write.writerow(header)
        write.writerow([pfx,tc,tcstd,m,mstd,l,lstd])


if __name__ == '__main__':
    exit(main())
