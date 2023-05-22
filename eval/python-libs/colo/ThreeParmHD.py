__all__ = ['ThreeParmHD']

import alive_progress # pip install alive-progress
import itertools
import logging
import math
import multiprocessing
import multiprocessing.dummy
import os
from .Helpers import *
from .Exact import TaskWCET

class ThreeParmHD(TaskWCET):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._thrd_tbl = None
        self._wcet_tbl = None        

    def sec_span(self, sec, m=None):
        pfx=self._title
        if m:
            self._cores = m

        # thrd_tbl[object name] = # of threads
        self._thrd_tbl = sec.threads_by_object()
        # wcet_tbl[object name] = wcet function
        self._wcet_tbl = sec.wcet_by_object()
        self.desc_tbl(self._thrd_tbl, self._wcet_tbl)

        # Calculate the lower bound
        LB = self.lowerbound(sec, m)

        # Perform the binary search with heuristic deadline
        accept = self.bin_search(sec, LB, LB * 3)
        if not accept:
            logging.warning(f'{pfx} Unable to find any schedule')
            raise RuntimeError

        # Results are stored in self._est_lengths and self._act_lengths
        makespan = max(self._act_lengths)
        descs = self._descs
        for i in range(m):
            descs[i] += f'<= {self._act_lengths[i]}'

        hd = '?'
        if hasattr(self, '_HD'):
            hd = self._HD
            del self._HD
        logging.info(f'{pfx} 3-Parm-HD Schedule with Heuristic '
                     f'Deadline:{hd}\n' + '\n'.join(descs))

        self._thrd_tbl = None
        self._wcet_tbl = None
        del self._act_lengths
        del self._est_lengths        
        del self._LB
        return makespan

    def lowerbound(self, sec, m):
        '''
        Calculates the lowerbound for a parallel section [sec]
        for [m] cores
        '''

        # thread_tbl[object name] = number of threads
        if not self._thrd_tbl:
            self._thrd_tbl = sec.threads_by_object()
        thread_tbl = self._thrd_tbl

        # wcet_tbl[object name] = wcet_fn
        if not self._wcet_tbl:
            self._wcet_tbl = sec.wcet_by_object()
        wcet_tbl = self._wcet_tbl

        # Find the average 
        heavy_max = 0
        wcet_total = 0
        for obj, threads in thread_tbl.items():
            wcetfn = wcet_tbl[obj]
            heavy_max = max(heavy_max, wcetfn(1))
            wcet_total += wcetfn(threads)
        wcet_avg = math.ceil(wcet_total / m)
        self._LB = max(heavy_max, wcet_avg)

        logging.info(f'{self._title} max heavy weight:{heavy_max} '
              f'total wcet:{wcet_total} avg over {m}: {wcet_avg}')
        logging.info(f'{self._title} lowerbound: {self._LB}')
        return self._LB

    def bin_search(self, sec, min_hd, max_hd, space=''):
        '''
        Binary search of heuristic deadline
        '''

        if min_hd >= max_hd:
            return False

        mid_hd = math.ceil((min_hd + max_hd) / 2)
        accept = self.sec_sched(sec, mid_hd)

        if not accept:
            # This heuristic deadline cannot be met
            # Increase the deadline and try again
            if self.bin_search(sec, mid_hd, max_hd, space + ' '):
                return True
            return False

        # This heuristic deadline can be met
        if mid_hd >= max_hd:
            # Cannot reduce the deadline
            return accept
        
        # Reduce the deadline and try again
        return self.bin_search(sec, min_hd, mid_hd, space + ' ')
    
    
    def sec_sched(self, sec, hd):
        # Create m schedules
        m = self._cores
        self._act_lengths = [0] * m
        self._est_lengths = [0] * m
        self._descs = [''] * m
        
        for i in range(m):
            self._descs[i] = f'S{i} | '

        core = 0
        for obj, threads in self._thrd_tbl.items():
            wcetfn = self._wcet_tbl[obj]
            try:
                core = self.assign_threads(core, obj, threads,
                                           wcetfn, hd)
            except StopIteration:
                return False
        self._HD = hd
        return True

    def assign_threads(self, core, O, T, C, hd):
        '''
        Assigns all [T] threads of object [O] to core schedules,
        starting with [core].

        Returns the [lastcore] threads were assigned to.

        in/out parameters:
          est_lengths - the estimated lengths used by the algorithm
          act_lengths - the actual lengths after assignment
          descs       - a description of the core schedules 
        '''
        act_lengths = self._act_lengths
        est_lengths = self._est_lengths
        descs = self._descs

        # tmp = descs.copy()
        # for i in range(self._cores):
        #     tmp[i] += f'<= {self._act_lengths[i]}'
        # logging.info(f'{self._title} BEFORE 3-Parm-HD Schedule with Heuristic '
        #              f'Deadline:{hd}\n' + '\n'.join(tmp))

        
        scheds = {core : 0}
        weight = C(1) # start with a heavy thread
        act_weight = weight
        for i in range(T):
            if (act_lengths[core] + weight) >= hd:
                # Increment the core
                core += 1
                act_weight = C(1)
                scheds[core] = 0
            if core >= self._cores:
                raise StopIteration
            if est_lengths[core] > self._LB:
                # Current schedule exceeds the lower bound, advance
                core += 1
                act_weight = C(1)
                scheds[core] = 0
            if core >= self._cores:
                raise StopIteration
            # Increase the number of objects on this core
            scheds[core] += 1
            est_lengths[core] += weight
            act_lengths[core] += act_weight
            if weight == C(1):
                # Only the first thread is heavy
                weight = C.incr
            if act_weight == C(1):
                act_weight = C.incr
            

        for core, threads in scheds.items():
            if threads == 0:
                continue
            demand = C(threads)
            descs[core] += f'{O}({threads}):{demand:<3}'

        # tmp = descs.copy()
        # for i in range(self._cores):
        #     tmp[i] += f'<= {self._act_lengths[i]}'
        # logging.info(f'{self._title} AFTER 3-Parm-HD Schedule with Heuristic '
        #              f'Deadline:{hd}\n' + '\n'.join(tmp))

            
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
        


