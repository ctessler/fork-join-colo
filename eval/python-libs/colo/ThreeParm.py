__all__ = ['ThreeParm']

import alive_progress # pip install alive-progress
import itertools
import logging
import math
import multiprocessing
import multiprocessing.dummy
import os
from .Helpers import *
from .Exact import TaskWCET

class ThreeParm(TaskWCET):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.lb = None

    def lowerbound(self, sec, m):
        '''
        Calculates the lowerbound for a parallel section [sec]
        for [m] cores
        '''

        # thread_tbl[object name] = number of threads
        thread_tbl = sec.threads_by_object()

        # wcet_tbl[object name] = wcet_fn
        wcet_tbl = sec.wcet_by_object()

        # Find the average 
        heavy_max = 0
        wcet_total = 0
        for obj, threads in thread_tbl.items():
            wcetfn = wcet_tbl[obj]
            heavy_max = max(heavy_max, wcetfn(1))
            wcet_total += wcetfn(threads)
        wcet_avg = math.ceil(wcet_total / m)
        self.lb = max(heavy_max, wcet_avg)

        logging.info(f'{self._title} max heavy weight:{heavy_max} '
              f'total wcet:{wcet_total} avg over {m}: {wcet_avg}')
        logging.info(f'{self._title} lowerbound: {self.lb}')
        return self.lb
    
    def sec_span(self, sec, m=None):
        pfx=self._title
        if m:
            self.cores = m
        if not self.cores:
            raise Exception('Number of cores is required')

        # Calculate the lower bound
        LB = self.lowerbound(sec, m)

        # thrd_tbl[object name] = # of threads
        thrd_tbl = sec.threads_by_object()
        # wcet_tbl[object name] = wcet function
        wcet_tbl = sec.wcet_by_object()
        self.desc_tbl(thrd_tbl, wcet_tbl)

        # Create m schedules
        est_lengths = [0] * m
        act_lengths = [0] * m
        descs = [''] * m
        core = 0
        for i in range(m):
            descs[i] = f'S{i} | '
        for obj, threads in thrd_tbl.items():
            wcetfn = wcet_tbl[obj]
            core = self.assign_threads(
                LB, est_lengths, act_lengths, descs, core,
                obj, wcetfn, threads)

        makespan = max(act_lengths)
        for i in range(m):
            descs[i] += f'<= {act_lengths[i]}'
        logging.info(f'{pfx} 3-Parm Schedule:\n' + '\n'.join(descs))
        
        return makespan, descs

    def assign_threads(self, LB, est_lengths, act_lengths, descs,
                       core, O, C, T):
        '''
        Assigns all [T] threads of object [O] to core schedules,
        starting with [core].

        Returns the [lastcore] threads were assigned to.

        in/out parameters:
          est_lengths - the estimated lengths used by the algorithm
          act_lengths - the actual lengths after assignment
          descs       - a description of the core schedules 
        '''
        m = len(est_lengths) - 1
        scheds = {core : 0}
        weight = C(1) # start with a heavy thread
        for i in range(T):
            if est_lengths[core] > LB:
                # Current schedule exceeds the lower bound, advance
                core += 1
                scheds[core] = 0
            # Increase the number of objects on this core
            scheds[core] += 1
            est_lengths[core] += weight
            if weight == C(1):
                # Only the first thread is heavy
                weight = C.incr

        for core, threads in scheds.items():
            if threads == 0:
                continue
            demand = C(threads)
            descs[core] += f'{O}({threads}):{demand:<3}'
            act_lengths[core] += demand

        return core

    def desc_tbl(self, thrd_tbl, wcet_tbl):
        # Informational table
        maxthread = max(thrd_tbl.values())
        desc = f'{self._title} Object/Thread/WCET Table:\nobject | threads | '
        for i in range(1, maxthread + 1):
            desc += f'c({i}) '
        desc += '\n' + '-' * 70
        for obj, threads in thrd_tbl.items():
            desc += '\n'
            desc += f'{obj:<6} | {threads:<7} | '
            for i in range(1,threads + 1):
                desc += f'{wcet_tbl[obj](i):<4} '
        logging.info(desc)
        


