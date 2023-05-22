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
import matplotlib.colors as mcolors
import numpy
import os
import pandas
import pathlib

def sanity_check(df):
    '''
    Looks for anomalies in the dataframe
    '''
    prune = []

    for method in gp.algs_exact():
        # Check if the exact methods were used in the run
        # If one is missing, the sanity check cannot be performed
        if not f'{method}-Sched' in df.columns:
            return
    
    for name, row in df.iterrows():
        deadline = row['Deadline']

        ewc_sched = row['ExactColo-Sched']
        enc_sched = row['ExactNoColo-Sched']
        tp_sched = row['3-Parm-Sched']
        tg_sched = row['2-Gram-Sched']
        hd_sched = row['3-Parm-HD-Sched']

        # Exact With Colocation vs Exact Without Colocation
        if not ewc_sched and enc_sched:
            msg = f'Task-{name} is not schedulable under the exact '
            msg += 'test with co-location, but *is* schedulable '
            msg += 'by the exact test without co-location'
            logging.warning(msg)

        # Exact Without Colocation vs 2-Gram
        if not enc_sched and tg_sched:
            msg = f'Task-{name} is not schedulable under the '
            msg += 'exact test without co-location, but *is* '
            msg += 'schedulable by the 2-Gram approximation'
            logging.warning(msg)            

        # Exact With Colocation vs 2-Gram
        if not ewc_sched and tg_sched:
            msg = f'Task-{name} is not schedulable under the '
            msg += 'exact test with co-location, but *is* '
            msg += 'schedulable by the 2-Gram approximation'
            logging.warning(msg)

        if not ewc_sched and hd_sched:
            msg = f'Task-{name} is not schedulable under the '
            msg += 'exact test with co-location, but *is* '
            msg += 'schedulable by the 3-Parm-HD approximation'
            logging.warning(msg)

        if not hd_sched and tp_sched:
            msg = f'Task-{name} is not schedulable under the '
            msg += '3-Parm-HD, but *is* '
            msg += 'schedulable by the 3-Parm approximation'
            logging.warning(msg)
            
def module_start(context_dir, skip_exact=False):
    '''
    Entry point when used as a module

    context_dir - the directory containing the results after they have
                  been processed by the WCET and scheduling algorithms 
    '''
    
    ctx_dir = os.path.normpath(context_dir)
    if not os.path.isdir(ctx_dir):
        raise NotADirectoryError(f'{ctx_dir} does not exist')

    task_csv = os.path.normpath(ctx_dir + '/tasks.csv')
    if not os.path.isfile(task_csv):
        raise FileNotFoundError(f'{task_csv} does not exist')

    graph_dir = os.path.normpath(ctx_dir + '/graphs')
    os.makedirs(graph_dir, exist_ok=True)

    df = pandas.read_csv(task_csv)
    df.set_index('Name', inplace=True)

    
    sanity_check(df)
    num_tasks = len(df.index)
    core_range = find_core_range(df)
    core_range_dag = dag_core_range(df)

    plt.rc('font', size=12, family='serif')

    print(f'Number of tasks:{num_tasks} Core range:{core_range}')
    print(f'Creating approximation and exact core allocation graphs')
    ae_core_allocation(graph_dir, df, num_tasks, core_range)
    print(f'Creating DAG core allocation graphs')
    dag_core_allocation(graph_dir, df, num_tasks, core_range_dag)
    print(f'Creating schedulability graphs')    
    schedulability(graph_dir, df, num_tasks, core_range)
    print(f'Creating timing graphs')        
    timing(graph_dir, df, num_tasks, core_range)
    print(f'Creating cache reuse graphs')            
    cache_reuse(graph_dir, df, num_tasks, core_range)
    print(f'Creating timing line graphs')
    timing_growth(graph_dir, df, num_tasks, core_range)
    timing_with_confidence(graph_dir, df)

    print(f'Creating Core Comparison Graphs')
    core_comp(graph_dir, df, num_tasks, core_range)

    df = pandas.DataFrame(None)
    return 0

def ae_core_allocation(graph_dir, df, num_tasks, core_range):
    algs = gp.algs_approx() + gp.algs_dag()
    if do_exact(df):
        algs = algs + gp.algs_exact()

    sf = {}
    for alg in algs:
        sched = gp.key_sched(alg)
        sf[alg] = df[df[sched] == True]

    cores = []
    labels = []
    colors = []
    for alg in algs:
        core = gp.key_cores(alg)
        cores.append(sf[alg][core])
        labels.append(gp.get_label(alg))
        colors.append(gp.get_color(alg))

    plt.hist(cores, label=labels, color=colors, edgecolor='black')
    plt.xticks(core_range)
    plt.ylabel('Number of Tasks Schedulable', fontsize=gp.axis_fontsize())
    plt.xlabel('Number of Required Cores', fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    path = os.path.normpath(graph_dir + '/ae-core-allocation.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    accum = {}
    for pfx in algs:
        accum[pfx] = []
        subf = sf[pfx]
        core = gp.key_cores(pfx)
        for m in core_range:
            count = len(subf[subf[core] <= m].index)
            accum[pfx].append(100 * (count / num_tasks))

    for pfx in algs:
        plt.plot(core_range, accum[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx, core_range))
    
    plt.legend(loc='best')
    xticks = core_range
    if len(xticks) > 10:
        xticks = range(0, core_range[-1] + 1, math.floor(core_range[-1] / 10))
    plt.xticks(xticks)
    plt.ylabel('Percentage of Tasks Schedulable\n'
               f'on {max(core_range)} or Fewer Cores',
               fontsize=gp.axis_fontsize())
    plt.xlabel('Number of Required Cores',
               fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/ae-core-allocation-agg.png')    
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def dag_core_allocation(graph_dir, df, num_tasks, core_range):
    sf = {}
    for pfx in gp.algs_dag():
        sched = gp.key_sched(pfx)
        sf[pfx] = df[df[sched] == True]

    cores = []
    labels = []
    colors = []
    for pfx in gp.algs_dag():
        core = gp.key_cores(pfx)
        cores.append(sf[pfx][core])
        labels.append(gp.get_label(pfx))
        colors.append(gp.get_color(pfx))
        
    plt.hist(cores, label=labels, color=colors)
    plt.ylabel('Number of Tasks Schedulable', fontsize=gp.axis_fontsize())
    plt.xlabel('Number of Required Cores', fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    path = os.path.normpath(graph_dir + '/dag-core-allocation.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    accum = {}
    step = math.ceil(len(core_range) / 10)
    tenth_range = core_range[0::step]
    for pfx in gp.algs_dag():
        accum[pfx] = []
        subf = sf[pfx]
        core = gp.key_cores(pfx)
        for m in tenth_range:
            count = len(subf[subf[core] <= m].index)
            accum[pfx].append(100 * (count / num_tasks))

    for pfx in gp.algs_dag():
        plt.plot(tenth_range, accum[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx))
    
    plt.legend(loc='best')
    xticks = tenth_range
    if len(xticks) > 10:
        xticks = range(0, core_range[-1] + 1, math.floor(core_range[-1] / 10))
    plt.ylabel('Percentage of Tasks Schedulable', fontsize=gp.axis_fontsize())
    plt.xlabel('Number of Required Cores', fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/dag-core-allocation-agg.png')    
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    
def schedulability(graph_dir, df, num_tasks, core_range):
    algs = gp.algs_approx() + gp.algs_dag()
    if do_exact(df):
        algs = algs + gp.algs_exact()

    sf = {}
    for pfx in algs:
        sched = gp.key_sched(pfx)
        sf[pfx] = df[sched]

    sums = []
    labels = []
    for pfx in algs:
        s = sf[pfx].values.sum()
        sums.append(s)
        labels.append(gp.get_label(pfx) + f' {s}')
        
    plt.bar(labels, sums, color=['red', 'blue', 'green'],
            align='edge', width=0.1)
    plt.ylabel(f'Tasks Schedulable on {max(core_range)} or Fewer Cores'
               f'\nTotal Tasks: {num_tasks}',
               fontsize=gp.axis_fontsize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.normpath(graph_dir + '/schedulability.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()


def timing_exact(graph_dir, df, num_tasks, core_range):
    exact = []
    exact_labels = []
    ymax = 0
    for pfx in gp.algs_exact():
        secs = f'{pfx}-Seconds'
        q25, med, q75 = df[secs].quantile([.25, .5, .75], interpolation='nearest').array
        med = df[secs].median()
        ub = q75 + 2 * (q75 - q25)
        ymax = max(ub, ymax)
        exact.append(df[secs])
        desc = f'{pfx}\nQs({q25:<0.2}, {med:<0.2}, {q75:<0.2})'
        exact_labels.append(desc)

    plt.boxplot(exact, labels = exact_labels)
    plt.ylabel('Completion Time in Seconds', fontsize=gp.axis_fontsize())
    plt.xlabel('Method', fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/timing-exact-nomax.png')
    plt.savefig(path, bbox_inches='tight')
    plt.ylim([0, ymax])
    path = os.path.normpath(graph_dir + '/timing-exact-limited.png')
    plt.savefig(path, bbox_inches='tight')    
    plt.close()
    
def timing_dag(graph_dir, df, num_tasks, core_range):
    dag = []
    dag_labels = []
    for pfx in gp.algs_dag():
        secs = gp.key_seconds(pfx)
        dag.append(df[secs])
        dag_labels.append(gp.get_label(pfx))

    plt.boxplot(dag, labels=dag_labels)
    plt.ylabel('Completion Time in Seconds', fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/timing-dag.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    
def timing(graph_dir, df, num_tasks, core_range):
    if not all([gp.key_sched(item) in df.columns for item in
            gp.algs_exact()]):
        logging.warning('skipping timing for exact methods')
    else:
        timing_exact(graph_dir, df, num_tasks, core_range)
        
    timing_dag(graph_dir, df, num_tasks, core_range)
    
    approx = []
    approx_labels = []
    for pfx in gp.algs_approx():
        secs = gp.key_seconds(pfx)
        approx.append(df[secs])
        approx_labels.append(gp.get_label(pfx))
    plt.boxplot(approx, labels = approx_labels)
    plt.ylabel('Completion Time in Seconds',
               fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/timing-approx.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    return


def timing_growth(graph_dir, df, numb_tasks, core_range):
    path = os.path.normpath(graph_dir + '/all-timing-growth.png')
    algs = gp.algs_approx() + gp.algs_dag()
    if do_exact(df):
        algs = algs + gp.algs_exact()

    # Approximate and Exact Methods
    data = {}
    labels = []
    for pfx in algs:
        labels.append(gp.get_label(pfx))
        data[pfx] = df.groupby('TotalThreads')[f'{pfx}-Seconds'].mean()

    trange = range(df['TotalThreads'].max() - df['TotalThreads'].min())
    for pfx in algs:
        plt.plot(data[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx, trange))
    plt.legend(loc='best')
    plt.xlabel('Threads per Task', fontsize=gp.axis_fontsize())
    plt.ylabel('Average Completion Time', fontsize=gp.axis_fontsize())
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    path = os.path.normpath(graph_dir + '/ae-timing-growth.png')
    for pfx in gp.algs_approx() + gp.algs_dag():
        plt.plot(data[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx, trange))
    plt.legend(loc='best')
    plt.xlabel('Threads per Task', fontsize=gp.axis_fontsize())
    plt.ylabel('Average Completion Time', fontsize=gp.axis_fontsize())
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def timing_with_confidence(graph_dir, df):
    path = os.path.normpath(graph_dir + '/timing-confidence.png')

    algs = gp.algs_approx() + gp.algs_dag()
    if do_exact(df):
        algs = algs + gp.algs_exact()

    maxt = range(df['TotalThreads'].max() - df['TotalThreads'].min())
    grouped = df.groupby('TotalThreads')
    for alg in algs:
        seckey = gp.key_sched(alg)

        stats = grouped[seckey].agg(['mean', 'count', 'std'])
        chi = []
        clo = []
        for i in stats.index:
            m, c, s = stats.loc[i]
            chi.append(m + 1.96*s/math.sqrt(c))
            clo.append(m - 1.96*s/math.sqrt(c))

        plt.plot(stats['mean'], label=gp.get_label(alg),
                 linestyle=gp.get_line(alg),
                 color=gp.get_color(alg),
                 marker=gp.get_marker(alg),
                 markersize=gp.get_markersize(alg),
                 markerfacecolor=gp.get_markerfacecolor(alg),
                 markevery=gp.get_markevery(alg, maxt))
        plt.fill_between(stats.index, clo, chi,
                         color=gp.get_color(alg),
                         alpha=.1,
                         interpolate=True)
    plt.legend(loc='best')
    plt.xlabel('Threads per Task', fontsize=gp.axis_fontsize())
    plt.ylabel('Average Completion Time', fontsize=gp.axis_fontsize())
    plt.savefig(path, bbox_inches='tight')
    logging.info(f'Writing {path}')
    plt.close()
    

def cache_reuse(graph_dir, df, num_tasks, core_range):
    sf = df[gp.task_key_reuse()].value_counts(bins=10, sort=False)

    labels = []
    for val in sf.index.values:
        labels.append(str(val))
    
    plt.bar(labels, sf.values,
            color=gp.get_color(None, bar=True), edgecolor='black')
    plt.xticks(rotation=45)
    plt.tight_layout()
    ticks = range(0, max(sf.values + 2))
    plt.xlabel(f'Cache Reuse Factor Interval', fontsize=gp.axis_fontsize())
    plt.ylabel(f'Number of Tasks', fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/cache-reuse.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    accum = []
    pct = []
    for label, count in zip(labels, sf.values):
        if len(accum) == 0:
            accum.append(count)
            pct.append(count / num_tasks)
            continue
        accum.append(count + accum[-1])
        pct.append(100 * (accum[-1] / num_tasks))

    labels=[]
    for pair in sf.index.values:
        labels.append(pair.right)
        
    plt.plot(labels, pct)
    plt.xlabel('Cache Reuse Factor', fontsize=gp.axis_fontsize())
    plt.ylabel('Percentage of All Tasks', fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/cache-reuse-agg.png')    
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    ca_sched(graph_dir, df, num_tasks, core_range, gp.algs_ordered(),
             'schedulability-cache-reuse-agg-all.png')
    ca_sched(graph_dir, df, num_tasks, core_range, gp.algs_approx(),
             'schedulability-cache-reuse-agg-approx.png')
    ca_sched(graph_dir, df, num_tasks, core_range, gp.algs_exact(),
             'schedulability-cache-reuse-agg-exact.png')
    ca_sched(graph_dir, df, num_tasks, core_range, gp.algs_dag(),
             'schedulability-cache-reuse-agg-dag.png')
    ca_pct(graph_dir, df, num_tasks, core_range, gp.algs_ordered(),
             'schedulability-cache-reuse-pct-all.png')
    ca_pct(graph_dir, df, num_tasks, core_range, gp.algs_approx(),
             'schedulability-cache-reuse-pct-approx.png')
    ca_pct(graph_dir, df, num_tasks, core_range, gp.algs_exact(),
             'schedulability-cache-reuse-pct-exact.png')
    ca_pct(graph_dir, df, num_tasks, core_range, gp.algs_dag(),
             'schedulability-cache-reuse-pct-dag.png')
    ca_count(graph_dir, df, num_tasks, core_range, gp.algs_ordered(),
             'schedulability-cache-reuse-count-all.png')
    ca_count(graph_dir, df, num_tasks, core_range, gp.algs_approx(),
             'schedulability-cache-reuse-count-approx.png')
    ca_count(graph_dir, df, num_tasks, core_range, gp.algs_exact(),
             'schedulability-cache-reuse-count-exact.png')
    ca_count(graph_dir, df, num_tasks, core_range, gp.algs_dag(),
             'schedulability-cache-reuse-count-dag.png')

def ca_sched(graph_dir, df, num_tasks, core_range, subset, png):
    sf = df[gp.task_key_reuse()].value_counts(bins=10, sort=False)

    if not all([gp.key_sched(item) in df.columns for item in subset]):
        logging.warning(f'ca_sched skipping {png}')
        return
    
    intmax=[]
    for pair in sf.index.values:
        intmax.append(pair.right)
    
    schedf = {}
    accum = {}
    for pfx in subset:
        col = f'{pfx}-Sched'
        subf = df[df[col] == True]
        col = f'{pfx}-Cores'
        subf = subf[subf[col] <= max(core_range)]
        schedf[pfx] = subf
        accum[pfx] = []
        for right in intmax:
            count = len(subf[subf[gp.task_key_reuse()] <= right].index)
            accum[pfx].append(100 * (count / num_tasks))
        
    for pfx in subset:
        plt.plot(intmax, accum[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx))
    
    plt.legend(loc='best')
    plt.xlabel('Cache Reuse Factor Upper Bound',
               fontsize=gp.axis_fontsize())
    plt.ylabel('Percentage of Tasks Schedulable\n'
               f'on {max(core_range)} or Fewer Cores',
               fontsize=gp.axis_fontsize())
    path = os.path.normpath(graph_dir + '/' + png)
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def ca_pct(graph_dir, df, num_tasks, core_range, subset, png):
    if not all([gp.key_sched(item) in df.columns for item in subset]):
        logging.warning(f'ca_pct skipping {png}')
        return
    
    cakey = gp.task_key_reuse()
    sf, bins = pandas.cut(df[cakey], bins=10, retbins=True)
    totalsf = df[cakey].value_counts(bins=bins, sort=False)
    labels = []
    for val in totalsf.index.values:
        left = val.left
        right = val.right
        if left < 0:
            left = 0.0
        labels.append(f'({left:<0.2f}, {right:<0.2f}]')
    
    accum = {}
    for pfx in subset:
        col = f'{pfx}-Sched'
        subf = df[df[col] == True]
        col = f'{pfx}-Cores'
        subf = subf[subf[col] <= max(core_range)]
        subf = subf[gp.task_key_reuse()].value_counts(bins=bins, sort=False)
        accum[pfx] = subf.divide(totalsf)
        accum[pfx] = accum[pfx].multiply(100)

    for pfx in subset:
        plt.plot(labels, accum[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx))
    
    # plt.legend(bbox_to_anchor=(0,1,1,0), loc='lower left',
    #     mode='expand', ncol=2)
    plt.legend(loc='best')
    plt.xlabel('Average Cache Reuse Factor Interval',
               fontsize=gp.axis_fontsize())
    plt.ylabel('Percentage of Tasks Schedulable\n'
               f'on {max(core_range)} or Fewer Cores',
               fontsize=gp.axis_fontsize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.normpath(graph_dir + '/' + png)
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def ca_count(graph_dir, df, num_tasks, core_range, subset, png):
    if not all([gp.key_sched(item) in df.columns for item in subset]):
        logging.warning(f'ca_count skipping {png}')
        return

    cakey = gp.task_key_reuse()
    sf, bins = pandas.cut(df[cakey], bins=10, retbins=True)
    totalsf = df[cakey].value_counts(bins=bins, sort=False)
    labels = []
    for val in totalsf.index.values:
        left = val.left
        right = val.right
        if left < 0:
            left = 0.0
        labels.append(f'({left:<0.2f}, {right:<0.2f}]')
    
    accum = {}

    for pfx in subset:
        col = f'{pfx}-Sched'
        subf = df[df[col] == True]
        col = f'{pfx}-Cores'
        subf = subf[subf[col] <= max(core_range)]
        subf = subf[gp.task_key_reuse()].value_counts(bins=bins, sort=False)
        if len(subf) != 0:
            accum[pfx] = subf
        else:
            logging.warning(f'{pfx} as *NO* schedulable tasks')
            logging.warning(f'SKIPPING ca_count for entire subset')
            return
            
    for pfx in subset:
        plt.plot(labels, accum[pfx], label=gp.get_label(pfx),
                 linestyle=gp.get_line(pfx),
                 color=gp.get_color(pfx),
                 marker=gp.get_marker(pfx),
                 markersize=gp.get_markersize(pfx),
                 markerfacecolor=gp.get_markerfacecolor(pfx),
                 markevery=gp.get_markevery(pfx))

    plt.legend(loc='best')
    plt.xlabel('Average Cache Reuse Factor Interval',
               fontsize=gp.axis_fontsize())
    plt.ylabel(f'Number of Tasks Schedulable\n'
               f'on {max(core_range)} or Fewer Cores',
               fontsize=gp.axis_fontsize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.normpath(graph_dir + '/' + png)
    plt.savefig(path, bbox_inches='tight')
    plt.close()


def core_comp(graph_dir, df, num_tasks, core_range):
    approx = gp.algs_approx()
    dag = gp.algs_dag()
    exact = gp.algs_exact()
    allalgs = gp.algs_ordered()

    if not do_exact(df):
        allalgs = dag + approx
        exact = []
    #
    # Dataframes by intersection
    # allsched -- tasks deemed schedulable by all algorithms
    # dagsched -- tasks deemed schedulable by the exact and DAG
    #             algorithms
    # aprsched -- tasks deemed schedulable by the approximate and
    #             exact algorithms

    allsched = df
    dagsched = df
    aprsched = df

    for a in allalgs:
        key = gp.key_sched(a)
        allsched = allsched.loc[allsched[key] == True]
    
    for a in dag + exact:
        key = gp.key_sched(a)
        dagsched = dagsched.loc[dagsched[key] == True]

    for a in approx + exact:
        key = gp.key_sched(a)
        aprsched = aprsched.loc[aprsched[key] == True]

    core_comp_helper(aprsched, approx + exact, core_range,
        os.path.normpath(graph_dir + '/sched-by-count-approx.png'))
    core_comp_helper(dagsched, dag + exact, core_range,
        os.path.normpath(graph_dir + '/sched-by-count-dag.png'))
    core_comp_helper(allsched, allalgs, core_range,
        os.path.normpath(graph_dir + '/sched-by-count-all.png'))
    core_comp_hist(aprsched, approx + exact, core_range,
        os.path.normpath(graph_dir + '/hist-sched-by-count-approx.png'))
    core_comp_hist(dagsched, dag + exact, core_range,
        os.path.normpath(graph_dir + '/hist-sched-by-count-dag.png'))
    core_comp_hist(allsched, allalgs, core_range,
        os.path.normpath(graph_dir + '/hist-sched-by-count-all.png'))
    core_comp_hist_pair(allsched, approx + exact, dag + exact, core_range,
        os.path.normpath(graph_dir + '/hist-sched-by-count-sbs.png'))

    core_comp_helper_cdf(aprsched, approx + exact, core_range,
        os.path.normpath(graph_dir + '/sched-by-count-cdf-approx.png'))
    core_comp_helper_cdf(dagsched, dag + exact, core_range,
        os.path.normpath(graph_dir + '/sched-by-count-cdf-dag.png'))
    core_comp_helper_cdf(allsched, allalgs, core_range,
        os.path.normpath(graph_dir + '/sched-by-count-cdf-all.png'))

def core_comp_helper(frame, algs, core_range, path):
    fig = plt.figure()
    plt.subplot2grid((1, 4), (0, 0), colspan=3)
    
    total_tasks = len(frame.index)
    means = []
    for alg in algs:
        counts = []
        key = gp.key_cores(alg)
        means.append(frame[key].mean())
        for core in core_range:
            sched = frame.loc[frame[key] == core]
            counts.append(len(sched.index))
        plt.plot(core_range, counts, label=alg,
                 color=gp.get_color(alg),
                 linestyle=gp.get_line(alg),
                 markevery=gp.get_markevery(alg, core_range),
                 markerfacecolor=gp.get_markerfacecolor(alg),
                 marker=gp.get_marker(alg),
                 markersize=gp.get_markersize(alg))

    plt.ylabel(f'Number of Tasks Schedulable',
               fontsize=gp.axis_fontsize())
    plt.xlabel(f'Number of Cores',
               fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    plt.title(f'Tasks in Intersection {total_tasks}')

    # Add the table
    columns = (['Mean\nCores'])
    colors = []
    text = []
    labels = []
    for (alg, mean) in zip(algs, means):
        text.append([f'{mean:.2f}'])
        colors.append(gp.get_markerfacecolor(alg))
        labels.append(gp.get_label(alg))
                       
    plt.subplot2grid((1, 4), (0, 3))    
    tbl= plt.table(cellText=text,
              rowLabels=labels,
              rowColours=colors,
              colLabels=columns,
                   cellLoc='center',
              loc='center',
              )

    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_height(.15)
            continue
        cell.set_height(.1)
    
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(gp.axis_fontsize() - 2)
    tbl.auto_set_column_width((0, -1))
    plt.axis('off')
    plt.subplots_adjust(left=.2)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logging.info(f'Wrote graph {path}')

def core_comp_helper_cdf(frame, algs, core_range, path):
    fig = plt.figure()
    plt.subplot2grid((1, 4), (0, 0), colspan=3)
    
    total_tasks = len(frame.index)
    means = []
    for alg in algs:
        counts = []
        key = gp.key_cores(alg)
        means.append(frame[key].mean())
        subtotal = 0
        for core in core_range:
            sched = frame.loc[frame[key] == core]
            subtotal += len(sched.index)
            counts.append(100 * subtotal / total_tasks)
        plt.plot(core_range, counts, label=alg,
                 color=gp.get_color(alg),
                 linestyle=gp.get_line(alg),
                 markevery=gp.get_markevery(alg, core_range),
                 markerfacecolor=gp.get_markerfacecolor(alg),
                 marker=gp.get_marker(alg),
                 markersize=gp.get_markersize(alg))

    plt.ylabel(f'Percentage of Tasks Schedulable\n'
               f'on {max(core_range)} or Fewer Cores',
               fontsize=gp.axis_fontsize())
    plt.xlabel(f'Number of Required Cores',
               fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    plt.title(f'Tasks in Intersection {total_tasks}')

    # Add the table
    columns = (['Mean\nCores'])
    colors = []
    text = []
    labels = []
    for (alg, mean) in zip(algs, means):
        text.append([f'{mean:.2f}'])
        colors.append(gp.get_markerfacecolor(alg))
        labels.append(gp.get_label(alg))
                       
    plt.subplot2grid((1, 4), (0, 3))    
    tbl= plt.table(cellText=text,
              rowLabels=labels,
              rowColours=colors,
              colLabels=columns,
                   cellLoc='center',
              loc='center',
              )

    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_height(.15)
            continue
        cell.set_height(.1)
    
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(gp.axis_fontsize() - 2)
    tbl.auto_set_column_width((0, -1))
    plt.axis('off')
    plt.subplots_adjust(left=.2)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logging.info(f'Wrote graph {path}')

def core_comp_hist(frame, algs, core_range, path):
    f = 1 / (len(algs) + 2)
    i = 1
    for alg in algs:
        counts = []
        key=alg + '-Cores'
        for core in core_range:
            eqsched = frame.loc[frame[key] == core]
            counts.append(len(eqsched.index))
        offset = f * i
        i += 1
        plt.bar([c + offset for c in core_range], counts, f,
                label=alg,
                capstyle='round',
                edgecolor='black',
                tick_label=alg,
                )

    plt.ylabel(f'Number of Tasks Schedulable',
               fontsize=gp.axis_fontsize())
    plt.xticks([c + .5 for c in core_range],
               fontsize=gp.axis_fontsize())
    plt.xlabel(f'Number of Cores', fontsize=gp.axis_fontsize())
    plt.legend(loc='best')
    # plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logging.info(f'Wrote graph {path}')
        
def core_comp_hist_pair(frame, approx, dag, core_range, path):
    if not do_exact(frame):
        logging.warning(f'core_comp_hist skipping {path}')
        return
    fig, ax = plt.subplots(1, 2, sharey=True, tight_layout=True)
    plt.sca(ax[0])
    plt.ylabel(f'Number of Tasks Schedulable',
               fontsize=gp.axis_fontsize())

    cmap = gp.get_color_dict()
    for (a, algs) in zip(ax, [approx, dag]):
        f = 1 / (len(algs) + 2)
        i = 1
        for alg in algs:
            counts = []
            key=alg + '-Cores'
            for core in core_range:
                eqsched = frame.loc[frame[key] == core]
                counts.append(len(eqsched.index))
            offset = f * i
            i += 1
            a.bar([c + offset for c in core_range], counts, f,
                      label=alg,
                      capstyle='round',
                      edgecolor='black',
                      color=cmap[alg],
                      tick_label=alg,
                      )
        plt.sca(a)
        plt.xticks([c + .5 for c in core_range], core_range)
        if algs == approx:
            fortext = '\nfor Approximations'
        else:
            fortext = '\nfor DAG Methods'
        
        plt.xlabel(f'Number of Cores {fortext}', fontsize=gp.axis_fontsize())

    handles = [a.get_legend_handles_labels() for a in ax]
    plots, labels = [sum(z, []) for z in zip(*handles)]
    # ExactColo and ExactNoColo are guaranteed to be found twice in
    # the labels, remove one of them
    for name in ('ExactColo', 'ExactNoColo'):
        idx = labels.index(name)
        plots.pop(idx)
        labels.pop(idx)
    
    fig.legend(plots, labels, loc='upper center',
               bbox_to_anchor=(.55, 1.2), ncol=3)
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    logging.info(f'Wrote graph {path}')
        

def get_sched_algs(df):
    '''
    Returns a list of the scheduling algorithms included in the
    datframe 
    '''
    scheds = df.filter(regex=".*-Cores")
    cores = list(scheds.columns)
    algs = [i[:-6] for i in cores]

    return algs
    

def do_exact(df):
    exact = [gp.key_cores(item) for item in gp.algs_exact()]
    return all(item in df.columns for item in exact)


    
def find_core_range(df):
    '''
    Determines the core range of the dataset based on the approximate
    and exact algorithms. The DAG approach is not included here.

    returns a range object
    '''
    cores = [gp.key_cores(item) for item in gp.algs_approx()]
    exact = [gp.key_cores(item) for item in gp.algs_exact()]
    if do_exact(df):
        exact.remove(gp.key_cores('DAG-m'))
        cores = cores + exact

    max_core = 0
    for core in cores:
        m = df[core].max()
        max_core = max(m, max_core)
    return range(1, max_core + 1)

def dag_core_range(df):
    '''
    Determines the core range of the dataset for DAG core calculation

    returns a range object
    '''
    cores = [gp.key_cores(item) for item in gp.algs_dag()]

    max_core = 0
    for core in cores:
        m = df[core].max()
        max_core = max(m, max_core)

    return range(1, max_core + 1)

def main():
    '''Entry point when used a script'''
    cargs = comargs.CommonArgs()

    return module_start(cargs.namespace.dir,
                        cargs.namespace.skip_exact)

if __name__ == '__main__':
    exit(main())
