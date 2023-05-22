#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import alive_progress
import comargs
import colo
import colo.GraphParms as gp
import json
import logging
import math
import matplotlib.pyplot as plt
import numpy
import os
import pandas
import pathlib

def module_start(output_dir, ctxdirs, ctxnames=None, skip_exact=False):
    '''
    Entry point when used as a module

    ctxdirs - orderer list of context directories to generate graphs from. 
    '''
    plt.rc('font', size=12, family='serif')
    
    if ctxnames == None:
        ctxnames = ctxdirs

    frames = []
    for ctxdir in ctxdirs:
        frames.append(load_frame(ctxdir))

    aex_range = aex_core_range(frames)
    dag_range = dag_core_range(frames)

    ctx = { 'odir' : output_dir,
            'frames' : frames,
            'names' : ctxnames } 
    tasks_by_reuse(ctx)
    avg_reuse_by_set(ctx)
    sched_by_set(ctx)
    pctsched_by_set(ctx)

    stats(ctx)
    
    return 0

def load_frame(ctxdir):
    '''Loads a dataframe from context directory containing tabulated data'''
    path = os.path.normpath(ctxdir)
    if not os.path.isdir(path):
        raise NotADirectoryError(f'{path} does not exist')

    csv = os.path.normpath(path + '/tasks.csv')
    logging.info(f'Loading {csv}')
    if not os.path.isfile(csv):
        raise FileNotFoundError(f'{csv} does not exist')

    frame = pandas.read_csv(csv)
    frame.set_index('Name', inplace=True)
    return frame

def aex_core_range(frames):
    '''
    Returns a core range for the Approximate and Exact methods

    frames -- the ordered list of data frames
    '''

    min = 0
    max = 0
    for frame in frames:
        allcores = frame.filter(regex=".*-Cores")
        dagcores = frame.filter(regex="DAG-.*-Cores")
        ae_cores = allcores.drop(columns=list(dagcores))
        frame_min = ae_cores.min().min()
        frame_max = ae_cores.max().max()
        logging.debug(f'frame min/max:{frame_min}/{frame_max}')
        if frame_min < min or min == 0:
            min = frame_min
        if frame_max > max:
            max = frame_max

    return range(min, max + 1)

def dag_core_range(frames):
    '''
    Returns a core range for the DAG methods

    frames -- the ordered list of data frames
    '''

    min = 0
    max = 0
    for frame in frames:
        dag_cores = frame.filter(regex="DAG-.*-Cores")
        frame_min = dag_cores.min().min()
        frame_max = dag_cores.max().max()
        logging.debug(f'frame min/max:{frame_min}/{frame_max}')
        if frame_min < min or min == 0:
            min = frame_min
        if frame_max > max:
            max = frame_max

    return range(min, max + 1)

def cache_reuse_intervals(frames):
    '''Finds the cache reuse interval among all data frames'''
    all_frames = pandas.concat(frames)
    bin_frame = all_frames[gp.task_key_reuse()].value_counts(
        bins=10, sort=False)
    ivals = []

    for p in bin_frame.index.values:
        left = p.left
        right = p.right
        if left < 0:
            left = 0
        ivals.append((left, right))

    logging.debug(f'Cache Reuse Intervals: {ivals}')
    return ivals

def cache_reuse_labels(rivals):
    '''Returns a list of labels for the cache reuse intervals'''
    labels = []
    for (left, right) in rivals:
        label = f'[{left:.3f}, {right:.3f})'
        labels.append(label)
    return labels

def tasks_by_reuse(ctx):
    '''Plots the number of tasks by their cache reuse interval'''
    
    (frames, names, odir) = list(map(ctx.get, ('frames', 'names', 'odir')))

    rivals = cache_reuse_intervals(frames)
    xlabels = cache_reuse_labels(rivals)

    all_counts = []
    for frame in frames:
        frame_counts = []
        for (left, right) in rivals:
            # Select rows within the interval
            count_frame = frame[(frame[gp.task_key_reuse()] >= left) &
                                (frame[gp.task_key_reuse()] < right)]
            # Count the rows and add them to the list
            frame_counts.append(len(count_frame))
        all_counts.append(frame_counts)

    for count, name in zip(all_counts, names):
        plt.plot(xlabels, count, label=name)
                 

    path = os.path.normpath(odir + '/tasks-by-reuse.png')
    plt.legend(loc='best')
    plt.ylabel('Number of Tasks', fontsize=gp.axis_fontsize())
    plt.xlabel('Cache Reuse Interval', fontsize=gp.axis_fontsize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    logging.info(f'Wrote graph {path}')
    return 0

def avg_reuse_by_set(ctx):
    '''Plots the average cache reuse factor of each task set'''
    (frames, names, odir) = list(map(ctx.get, ('frames', 'names', 'odir')))

    avgs = []
    for (frame, name) in zip(frames, names):
        avgs.append(frame[gp.task_key_reuse()].mean())

    plt.bar(names, avgs, color=gp.get_color(None, bar=True),
            edgecolor='black')

    plt.ylabel('Average Cache Reuse Factor', fontsize=gp.axis_fontsize())
    plt.xlabel('Task Set', fontsize=gp.axis_fontsize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.normpath(odir + '/avg-reuse-by-set.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    logging.info(f'Wrote graph {path}')    
    return 0

def sched_by_set(ctx):
    '''Plots the average cache reuse factor of each task set'''
    (frames, names, odir) = list(map(ctx.get, ('frames', 'names', 'odir')))

    # verify all task counts are correct
    ntasks = len(frames[0].index)
    for frame in frames:
        if ntasks != len(frame.index):
            raise Exception(f'Differing number of tasks')

    core_range = aex_core_range(frames)
    algs = list(frame.filter(regex=".*-Cores").columns)

    allcores = frame.filter(regex=".*-Cores")
    dagcores = frame.filter(regex="DAG-.*-Cores")
    ae_cores = allcores.drop(columns=list(dagcores))
    algs = list(ae_cores.columns)
    
    plt.xticks(range(len(names)), labels=names)
    for core in algs:
        counts = []
        aname=core[:-6]
        key=gp.key_sched(aname)
        for frame in frames:
            sched = frame[(frame[key] == True) &
                          (frame[core] > 0) &
                          (frame[core] <= max(core_range))]
            counts.append(len(sched.index))
        
        plt.plot(names, counts, label=gp.get_label(aname),
                 color=gp.get_color(aname),
                 marker=gp.get_marker(aname),
                 markerfacecolor=gp.get_markerfacecolor(aname),
                 markersize=gp.get_markersize(aname))
        
    plt.ylabel(f'Number of Schedulable Tasks\non {core_range[-1]} cores',
               fontsize=gp.axis_fontsize())
    plt.xlabel(f'Task Set', fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    plt.tight_layout()
    path = os.path.normpath(odir + '/sched-count-by-set.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    logging.info(f'Wrote graph {path}')
    return 0

def pctsched_by_set(ctx):
    '''Plots the average cache reuse factor of each task set'''
    (frames, names, odir) = list(map(ctx.get, ('frames', 'names', 'odir')))

    # verify all task counts are correct
    ntasks = len(frames[0].index)
    for frame in frames:
        if ntasks != len(frame.index):
            raise Exception(f'Differing number of tasks')

    core_range = aex_core_range(frames)
    algs = list(frame.filter(regex=".*-Cores").columns)

    allcores = frame.filter(regex=".*-Cores")
    dagcores = frame.filter(regex="DAG-.*-Cores")
    ae_cores = allcores.drop(columns=list(dagcores))
    algs = list(ae_cores.columns)
    
    plt.xticks(range(len(names)), labels=names)
    for core in algs:
        counts = []
        aname=core[:-6]
        key=gp.key_sched(aname)
        for frame in frames:
            sched = frame[(frame[key] == True) &
                          (frame[core] > 0) &
                          (frame[core] <= max(core_range))]
            counts.append(100 * len(sched.index) / ntasks)
        
        plt.plot(names, counts, label=gp.get_label(aname),
                 color=gp.get_color(aname),
                 marker=gp.get_marker(aname),
                 markerfacecolor=gp.get_markerfacecolor(aname),
                 markersize=gp.get_markersize(aname))
        
    plt.ylabel(f'Percentage of Schedulable Tasks on {core_range[-1]} cores',
               fontsize=gp.axis_fontsize())
    plt.xlabel(f'Task Set', fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    plt.tight_layout()
    path = os.path.normpath(odir + '/pctsched-count-by-set.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    logging.info(f'Wrote graph {path}')
    return 0

def stats(ctx):
    '''Plots the average cache reuse factor of each task set'''
    (frames, names, odir) = list(map(ctx.get, ('frames', 'names', 'odir')))

    deadlines = sorted(frames[0]['Deadline'].unique())

def opt_args():
    parser = argparse.ArgumentParser(
        description='',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dirs', action='append', nargs='+',
                       help='A context directory, containing the task'
                       'sets and results')
    parser.add_argument('-o', '--output-dir', type=str,
                        help='Directory to store the produced graphs',
                        default='.')

    return parser

def main():
    '''Entry point when used a script'''
    parser = opt_args()
    cargs = comargs.CommonArgs(parser)

    print(cargs.namespace.dir)

    return module_start(cargs.namespace.output_dir,
                        *cargs.namespace.dirs,
                        *cargs.namespace.dirs,
                        cargs.namespace.skip_exact)

if __name__ == '__main__':
    exit(main())
