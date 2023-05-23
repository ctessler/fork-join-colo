#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import colo
import colo.GraphParms as gp
import glob
import json
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

    fname = glob.glob('*.json')[0]
    with open(fname, 'r') as fp:
        task = json.load(fp, cls=colo.ForkJoinTaskDecoder)
    composite(df, task, 'mrtc-composite.png')
    composite(df, task, 'mrtc-composite.eps')
    return

def composite(dataf, task, filename):
    # Organize the data
    algs = dataf['Alg.']
    max1k=r'${max_1}$'
    mspank=r'${\Lambda}$'
    subd = {
        max1k : [],
        mspank : []
    }
    fillc = [
        '#d9d9d6',
        '#80adad'
    ]
    toppers = [
        [], #max1k go here
        []  #mspank go here
    ]

    labels = []
    ymax = dataf['Longest.Schd'].max()
    for alg in algs:
        # Get the data (max1, makespan, cores)
        max1 = dataf[dataf['Alg.'] == alg]['Longest.Schd'].iloc[0]
        mspan = task.get_result(alg + '-WCET')
        cores = task.get_result(alg + '-Cores')
        if mspan > task.deadline:
            cores = '> ' + f'{cores}'
        # Multiply because the synthetic tasks are scaled by 10^3
        mspan *= 1000
        ymax = max(ymax, mspan)
        subd[max1k].append(max1)
        toppers[0].append(max1)
        subd[mspank].append(mspan)
        toppers[1].append('Cores ' + r'${' + str(cores) + r'}$')
        labels.append(gp.get_label(alg) + '\nCores ' + r'${' + str(cores) + r'}$')
    ymax = max(ymax, task.deadline * 1000)
    ymax *= 1.2

    # Plot the data
    x = numpy.arange(len(labels))
    barw = 0.3
    m = 0
    fig, ax = plt.subplots(layout='constrained')
    for attr, val in subd.items():
        off = barw * m
        rects = ax.bar(x + off, val, barw, label=attr, color=fillc[m], edgecolor='black')
        # This puts the cores and cycles at the tops of the bars
        # but it's more confusing
        # for r in rects:
        #     top = toppers[m].pop(0)
        #     plt.text(r.get_x() + .05 * r.get_width(), r.get_y() + r.get_height() * 1.05, top,
        #              fontsize=gp.axis_fontsize(), rotation=40)
        m += 1




    ax.tick_params(labelsize=gp.axis_fontsize())
    ax.set_xticks(x + barw, labels, fontsize=gp.axis_fontsize())
    ax.set_ylim(0, ymax)
    plt.ylabel('Cycles', fontsize=gp.axis_fontsize())

    # Plot the deadline
    plt.axhline(y=task.deadline * 1000, label='Deadline', linestyle='--')

    ax.legend(loc='upper right', ncols=2, fontsize=gp.axis_fontsize())

    handles, labels = plt.gca().get_legend_handles_labels()
    order = [1, 0, 2]
    plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order],
               ncols=2, fontsize=gp.axis_fontsize())

    plt.savefig(filename, bbox_inches='tight', pad_inches=0.3)
    plt.close()





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

    bars = plt.bar(labels, dataf['Longest.Schd'], color=colors, edgecolor='black')
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

    bars = plt.bar(labels, dataf['Misses.Avg'], color=colors, edgecolor='black')
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

    bars = plt.bar(labels, dataf['Total.Cycles.Avg'], color=colors, edgecolor='black')
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
