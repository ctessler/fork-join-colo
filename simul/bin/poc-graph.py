#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import colo.GraphParms as gp
import logging
import matplotlib.pyplot as plt
import pandas
import numpy

def arguments():
    '''
    Parses the arguments from the command line

    returns an argparse.ArgumentParser.parse_args() object
    '''
    fclass = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=fclass)

    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Increase the logging level')
    parser.add_argument('datacsv', type=str, action='store',
                        help='Path to the data file')

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

def modstart(csvfile):
    plt.rcParams['text.usetex'] = True
    df = pandas.read_csv(csvfile)

    plt.rc('font', size=12, family='serif')

    mean_misses(df, 'mrtc-mean-misses.png')
    mean_misses(df, 'mrtc-mean-misses.eps')

    mean_cycles(df, 'mrtc-mean-cycles.png')
    mean_cycles(df, 'mrtc-mean-cycles.eps')

    max1_cycles(df, 'mrtc-max1-cycles.png')
    max1_cycles(df, 'mrtc-max1-cycles.eps')
    return

def max1_cycles(dataf, filename):
    #
    # dataf must have Alg. Longest.Sched, Longest.SDev
    #
    # save the figure size
    pres = plt.rcParams['figure.figsize']
    plt.rcParams['figure.figsize'] = (3,5)
    plt.xlabel('Approximation', fontsize=gp.axis_fontsize())
    plt.ylabel('Max Schedule Cycles ' + r'${max_1}$', fontsize=gp.axis_fontsize())

    labels = []
    colors = []
    stdevs = []
    for alg in dataf['Alg.']:
        real = dataf[dataf['Alg.'] == alg]['Longest.SDev'].iloc[0]
        stdevs.append(r'${\sigma :' + f'{real:.2f}' + '}$')
        labels.append(gp.get_label(alg))
        colors.append(gp.get_color(alg))

    bars = plt.bar(labels, dataf['Longest.Schd'], color=colors)
    for bar, stdev in zip(bars, stdevs):
        y = bar.get_height()
        plt.text(bar.get_x(), y + 5000, stdev)

    plt.savefig(filename, bbox_inches='tight')

    # restore the figure size
    plt.rcParams['figure.figsize'] = pres
    plt.close()


def mean_misses(dataf, filename):
    #
    # dataf must have Alg. Misses.Avg and Misses.SDev
    #
    # save the figure size
    pres = plt.rcParams['figure.figsize']
    plt.rcParams['figure.figsize'] = (3,5)
    plt.xlabel('Approximation', fontsize=gp.axis_fontsize())
    plt.ylabel('Mean Cache Misses ' + r'${miss_\mu}$', fontsize=gp.axis_fontsize())

    labels = []
    colors = []
    stdevs = []
    for alg in dataf['Alg.']:
        real = dataf[dataf['Alg.'] == alg]['Misses.SDev'].iloc[0]
        stdevs.append(r'${\sigma :' + f'{real:.2f}' + '}$')
        labels.append(gp.get_label(alg))
        colors.append(gp.get_color(alg))

    bars = plt.bar(labels, dataf['Misses.Avg'], color=colors)
    for bar, stdev in zip(bars, stdevs):
        y = bar.get_height()
        plt.text(bar.get_x(), y + 10, stdev)

    plt.savefig(filename, bbox_inches='tight')

    # restore the figure size
    plt.rcParams['figure.figsize'] = pres
    plt.close()


def mean_cycles(dataf, filename):
    #
    # dataf must have Alg. Total.Cycles.Avg and Total.Cycles.SDev
    #
    # save the figure size
    pres = plt.rcParams['figure.figsize']

    plt.rcParams['figure.figsize'] = (3,5)
    plt.xlabel('Approximation', fontsize=gp.axis_fontsize())
    plt.ylabel('Mean Total Cycles ' + r'${W_\mu}$', fontsize=gp.axis_fontsize())

    labels = []
    colors = []
    stdevs = []
    for alg in dataf['Alg.']:
        real = dataf[dataf['Alg.'] == alg]['Total.Cycles.SDev'].iloc[0]
        stdevs.append(r'${\sigma :' + f'{real:.2f}' + '}$')
        labels.append(gp.get_label(alg))
        colors.append(gp.get_color(alg))

    bars = plt.bar(labels, dataf['Total.Cycles.Avg'], color=colors)
    for bar, stdev in zip(bars, stdevs):
        y = bar.get_height()
        plt.text(bar.get_x(), y + 50000, stdev)

    plt.savefig(filename, bbox_inches='tight')
    # restore the figure size
    plt.rcParams['figure.figsize'] = pres
    plt.close()


def main():
    args = arguments()
    init_logging(args.verbose)
    res = modstart(args.datacsv)

    pass

if __name__ == '__main__':
    exit(main())
