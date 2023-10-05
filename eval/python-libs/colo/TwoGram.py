__all__ = ['TwoGram']

import alive_progress # pip install alive-progress
import itertools
import logging
import math
import multiprocessing
import multiprocessing.dummy
import os
from .Helpers import *
from .Exact import TaskWCET

class TwoGram(TaskWCET):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.heavy_tbl = {}
        self.thread_tbl = {}
        self.lb = None

    def lowerbound(self, sec, m):
        '''
        Calculates the lowerbound for a parallel section [sec]
        for [m] cores
        '''

        # thread_tbl[object name] = number of threads
        self.thread_tbl = sec.threads_by_object()

        # wcet_tbl[object name] = wcet_fn
        wcet_tbl = sec.wcet_by_object()

        # Construct the heavy table
        demand = 0
        heavy_max = 0
        for obj, threads in self.thread_tbl.items():
            wcet_fn = wcet_tbl[obj]
            wcet_one = wcet_fn(1)
            heavy_max = max(heavy_max, wcet_one)
            self.heavy_tbl[obj] = wcet_one
            demand += wcet_one * threads
        wcet_avg = math.ceil(demand / m)
        self.lb = max(heavy_max, wcet_avg)

        logging.info(f'{self._title} max heavy weight:{heavy_max} '
              f'total wcet:{demand} avg over {m}: {wcet_avg}')
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
        self.desc_tbl(self.thread_tbl, self.heavy_tbl)

        # Create m schedules
        scheds = [0] * m
        descs  = [''] * m
        for i in range(m):
            descs[i] = f'S{i} | '

        for obj, threads in self.thread_tbl.items():
            heavy_wcet = self.heavy_tbl[obj]
            for i in range(threads):
                min_idx = self.find_min_idx(scheds)
                scheds[min_idx] += heavy_wcet
                descs[min_idx] += f'{obj}(1):{heavy_wcet:<3}'

        makespan = max(scheds)
        for i in range(m):
            descs[i] += f'<= {scheds[i]}'
        logging.info(f'{pfx} 2-Gram Schedule:\n' + '\n'.join(descs))
        self.heavy_tbl = {}
        self.thread_tbl = {}

        return makespan, descs

    def find_min_idx(self, scheds):
        min_idx = 0
        for i in range(len(scheds)):
            if scheds[i] == 0:
                min_idx = i
                break
            if scheds[i] < scheds[min_idx]:
                min_idx = i
        return min_idx

    def desc_tbl(self, thrd_tbl, heavy_tbl):
        # Informational table
        maxthread = max(thrd_tbl.values())
        desc =  f'{self._title} (Object, Threads, WCET(1), '
        desc += f'WCET(1) * Thread Count) Table'
        desc += f'\nobject | threads | c(1) | c(1) * threads'
        desc += '\n' + '-' * 70
        for obj, threads in thrd_tbl.items():
            wcet_one = heavy_tbl[obj]
            desc += '\n'
            desc += f'{obj:>6} | {threads:>7} | {wcet_one:>4} | '
            desc += f'{wcet_one * threads:>4}'
        logging.info(desc)
        


