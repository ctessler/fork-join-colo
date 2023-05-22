#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import math

DFLT = {
    'ass' : 2,
    'cache_way_size' : 0x2000,
    'cpi' : 1,
    'brt' : 2048,
    'pfx' : 'sobj',
    'blck_bytes' : 32,
    'insn_bytes' : 4,
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
    parser.add_argument('-n', '--associativity', type=int,
                        default=DFLT['ass'],
                        help='Number of cache ways (associativity)')
    parser.add_argument('-s', '--cache-way-size', type=int,
                        default=DFLT['cache_way_size'],
                        help='The number of bytes per cache way')
    parser.add_argument('--block-bytes', type=int, action='store',
                        default=DFLT['blck_bytes'],
                        help='The number of bytes per cache block')
    parser.add_argument('--insn-bytes', type=int, action='store',
                        default=DFLT['insn_bytes'],
                        help='The number of bytes per instruction')
    parser.add_argument('base', type=int, action='store',
                        help='The base cost in number of cycles')
    parser.add_argument('incr', type=float, action='store',
                        help='The incremental cost as a percentage')
    parser.add_argument('pfx', type=str, action='store',
                        default=DFLT['pfx'], nargs='?',
                        help='Prefix for the output files')

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


def modstart(base, incr, pfx, cpi, brt, ways, block_bytes, insn_bytes,
             cache_way_size):
    '''
    Module entry point
    pfx  - prefix for the output files
    cpi  - constant for cycles per instruction
    brt  - constant for block reload time
    blck_bytes - bytes per cache block
    insn_bytes - bytes per instruction
    '''
    # number of splits
    splits = 2 * ways
    logging.debug(f'Number of splits: {splits}')

    # instructions per block
    ipb = math.ceil(block_bytes / insn_bytes)
    logging.debug(f'Instructions per block: {ipb}')

    # cycles per block
    cpb = brt + cpi * ipb
    logging.debug(f'Cycles per block: {cpb}')

    # blocks of base
    bob = math.ceil(base / cpb)
    logging.debug(f'Blocks of base: {bob}')

    # blocks evicted
    be = math.ceil(bob * incr)
    logging.debug(f'Blocks evicted: {be}')

    # blocks persisted
    bp = bob - be
    logging.debug(f'Blocks persisted: {bp}')

    # blocks per split
    bps = math.ceil(be / splits)
    logging.debug(f'Blocks per split: {bps}')

    # instructions per split
    ips = bps * ipb
    logging.debug(f'Instructions per split: {ips}')

    # bytes per split
    splitbytes = ips * insn_bytes
    if (splitbytes > cache_way_size):
        logging.warning(f'Number of bytes per split exceeds cach way size')
        logging.warning(f'{splitbytes:>25} > {cache_way_size}')
        newsplits = math.ceil((splitbytes * splits) / cache_way_size)
        splits = newsplits
        bps = math.ceil(be / splits)
        ips = bps * ipb
        logging.warning(f'*new* Number of splits: {splits}')
        logging.warning(f'*new* Blocks per split: {bps}')
        logging.warning(f'*new* Instructions per split: {ips}')
        splitbytes = ips * insn_bytes
    logging.debug(f'Bytes per split: {splitbytes}')


    # instructions persisted
    ip = bp * ipb
    logging.debug(f'Instructions persisted: {ip}')

    # bytes persisted
    bytesp = ip * insn_bytes;
    if (bytesp > cache_way_size):
        logging.error(f'Number of bytes persisted exceeds cache way size')
        logging.error(f'{bytesp:>25} > {cache_way_size}')
        exit(1)
    logging.debug(f'Bytes persisted: {bytesp}')

    ldpart(pfx, splits, cache_way_size)
    cpart(pfx, splits, ips, ip);

def ldpart(pfx, splits, way_bytes):
    '''
    Creates the linker portion for the functions

    pfx       -- the prefix of the filename to use for the linker
                 script part
    splits    -- the number of splits
    way_bytes -- the number of bytes per cache way
    '''
    with open(f'{pfx}-part.ld', mode='w') as ofile:
        for s in range(splits):
            # section identifier
            ofile.write(f'.{pfx}-{s} :\n')
            ofile.write( '{\n')
            ofile.write(f'    . = ALIGN(0x{way_bytes:0x});\n')
            ofile.write(f'    *(.{pfx}-{s}*)\n')
            ofile.write( '}\n')
        ofile.write(f'.{pfx}-persist :\n')
        ofile.write( '{\n')
        ofile.write(f'    . = ALIGN(0x{way_bytes:0x});\n')
        ofile.write(f'    *(.{pfx}-{s}*)\n')
        ofile.write( '}\n')

def cpart(pfx, splits, ips, ip):
    '''
    Creates the C source files

    pfx    -- the prefix of the file name
    splits -- the number of splits
    ips    -- instructions per split
    ip     -- instructions persisted
    '''
    with open(f'{pfx}-obj.c', mode='w') as ofile:
        for s in range(splits):
            csplit(ofile, pfx, s, ips)
        cpers(ofile, pfx, ip)
        ofile.write(f'void {pfx}(void) {{\n')
        for s in range(splits):
            ofile.write(f'\t{pfx}_p{s}();\n')
        ofile.write(f'\t{pfx}_persist();\n')
        ofile.write( '}\n')

def csplit(ofile, pfx, split, ips):
    '''
    Creates split different functions each ips instructions long.
    '''
    attr=f'__attribute__((__section__(".{pfx}-{split}")))'
    ofile.write(f'void {attr} {pfx}_p{split}(void) {{\n')
    ofile.write(f'\t//{ips} instructions\n')
    for i in range(ips):
        ofile.write('\tasm("add a0,zero,zero");\n')
    ofile.write( '}\n')

def cpers(ofile, pfx, ip):
    '''
    Creates a persistent function ip instructions long
    '''
    attr=f'__attribute__((__section__(".{pfx}-persist")))'
    ofile.write(f'void {attr} {pfx}_persist(void) {{\n')
    ofile.write(f'\t//{ip} instructions\n')
    for i in range(ip):
        ofile.write('\tasm("add a0,zero,zero");\n')
    ofile.write( '}\n')



def main():
    '''
    Script entry point

    Determines the layout of a synthetic object, producing the linker
    script definitions as well as the functions.

    '''
    args = arguments()
    init_logging(args.verbose)
    modstart(args.base, args.incr, args.pfx, args.cpi, args.brt,
             args.associativity, args.block_bytes, args.insn_bytes,
             args.cache_way_size)


if __name__ == '__main__':
    exit(main())
