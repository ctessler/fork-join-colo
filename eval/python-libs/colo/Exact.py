__all__ = ['ExactNoColo',
           'ExactColo',
           'TaskWCET']

import alive_progress # pip install alive-progress
import itertools
import logging
import math
import multiprocessing
import multiprocessing.dummy
import os
import queue
import signal
from .Helpers import *

PARALLEL_CHUNK = 2 ** 10
PARALLEL_CHUNK = 2 ** 12

class TaskWCET:
    def __init__(self, t=None, m=None):
        '''
        Constructor

        t: the task
        m: the number of cores
        '''
        self.task = t
        self.cores = m

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, t):
        self._task = t

    @property
    def cores(self):
        return self._cores

    @cores.setter
    def cores(self, m):
        self._cores = m

    def wcet(self, m=None, parallel=True):
        '''
        Returns the task's WCET for m cores for the given algorithm

        When parallel is False, use a single process.
        '''
        self._parallel=parallel
        
        t = self.task
        if not m:
            m = self.cores
        self.cores = m

        count=0
        makespans = []
        wcet = t.serial_wcet
        logging.info(f'Task:{t.name} Sections:{len(t.sections):<2} '
                     f'Sequential WCET:{t.serial_wcet}')
        for sec in t.sections:
            count += 1
            self._title = f'T:{t.name} Sec[{count}/{len(t.sections)}]'
            logging.info(f'{self._title} m:{m} nodes:{len(sec.nodes)}'
                         f' objects:{len(sec.objects)}')
            try:
                makespan = self.sec_span(sec, m)
            except KeyboardInterrupt:
                makespan = None

            if not makespan:
                raise KeyboardInterrupt('Yo')
            makespans.append(makespan)

            logging.info(f'{self._title} makespan:{makespan}')
            wcet += makespan

        logging.info(f'Task:{t.name} (fork/join bound) ⇶ '
              f'[sec bound] → (f/j) ⇶ [sec] ... ')
        wcet_str = ''
        desc = ''
        for fjnode, sec, span in \
            zip(t.serial_nodes, t.sections, makespans):
            wcet_str += f'{fjnode.bound()} + {span} + '
            desc += f'({fjnode.bound()}) ⇶ [{span}] → '
        last = t.serial_nodes[-1]
        desc += f'({last.bound()})'
        logging.info(desc)
        wcet_str += f'{last.bound()} = {wcet}'
        logging.info(f'Result:\n' +
                     f'┌\n' +
                     f'│ Task:{t.name} demand:{t.demand()} ' +
                     f'{m}-core WCET: {wcet_str} \n' +
                     f'└')
        return wcet

    def sec_span(self, sec, m=None):
        '''
        Returns the makespan for the parallel (sec)tion when
        allocatde m cores
        '''
        raise NotImplementedError

class ExactNoColo(TaskWCET):
    def setup(shutdown_evt, data_q):
        global g_shutdown
        global g_q
        g_shutdown = shutdown_evt
        g_q = data_q
    
    def sec_span(self, sec, m=None):
        pfx = self._title
        if not m:
            m = self.cores
        self.cores = m

        manager = multiprocessing.Manager()
        workq = multiprocessing.Queue(PARALLEL_CHUNK)
        shutdown_evt = manager.Event()

        itbyobj = {}
        total = 1
        tot_threads = 0
        for obj, threads in sec.threads_by_object().items():
            tot_threads += threads
            iterator = idiot(threads, m)
            total *= iterator.length()
            itbyobj[obj] = iterator
        procs = min(os.cpu_count(), total)
        step = math.ceil(total / procs)

        cross = itertools.product(*itbyobj.values())
        logging.info(f'  | Cores:{m} 1-Threaded-Objects:{tot_threads} '
                     f'Total Schedules:{total} Procesess:{procs}')

        self.desc_tbl(sec.threads_by_object(), sec.wcet_by_object())

        data = []
        for p in range(procs):
            start = p * step
            stop = (p + 1) * step
            cross, copy = itertools.tee(cross)
            iterables = itertools.islice(copy, start, stop)
            data.append([iterables, sec])

        # Handle SIGINT
        def handler(signum, frame):
            shutdown_evt.set()
        signal.signal(signal.SIGINT, handler)
            
        makespans = None
        with multiprocessing.Pool(procs, ExactNoColo.setup,
                                  (shutdown_evt, workq)) as pool:
            results = pool.starmap_async(self.span_job_ll, data)
            title=f'{self._title}'
            with alive_progress.alive_bar(total, title=title,
              length=20, bar='filling', spinner='dots_waves') as bar:
                for i in range(total):
                    if shutdown_evt.is_set():
                        break
                    finished = workq.get()
                    bar(finished)
                    # alive_progress.alive_bar doesn't do simple math
                    total = total - finished
                    if total <= 0:
                        break
            aresults = []
            if not shutdown_evt.is_set():
                aresults = results.get()
            else:
                pool.close()
                pool.terminate()
                item = 1
                while item:
                    try:
                        item = workq.get(block=False)
                    except queue.Empty:
                        break
            makespan = None
            desc = 'Terminated'
            for span, descr in aresults:
                if not span:
                    continue
                if not makespan or span < makespan:
                    makespan = span
                    desc = descr
        workq.close()
        workq.join_thread()

        for p in multiprocessing.active_children():
            while p.is_alive():
                p.terminate()
        
        print(f'{pfx} Minimum makespan schedule:')
        print(desc)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        return makespan

    def span_job_ll(self, iterable, sec):
        step = PARALLEL_CHUNK
        
        count = 0
        min_makespan = None
        descrs = []
        for a in iterable:
            lengths = [0] * self.cores
            descr = [''] * self.cores
            for obj, omap in zip(sec.objects, a):
                for idx in range(self.cores):
                    name = obj.name
                    threads = omap[idx]
                    if threads == 0:
                        continue
                    wcet = obj.wcet_fn(1) * threads
                    lengths[idx] += wcet
                    descr[idx] += f'{name:<2}({threads}):{obj.wcet_fn(1) * threads:<3}'
            # core schedules have been bounded

            # Update the minimum makespan
            span = max(lengths)
            if not min_makespan or span < min_makespan:
                min_makespan = span
                descrs = []
                for i in range(self.cores):
                    descrs.append(f'S{i} | ' + descr[i] + f'≤ {lengths[i]}')

            count += 1
            if (count == step):
                g_q.put(count)
                count = 0
        if count != 0:
            g_q.put(count)

        return min_makespan, '\n'.join(descrs)

    def desc_tbl(self, thrd_tbl, wcet_tbl):
        # Informational table
        maxthread = max(thrd_tbl.values())
        desc =  f'{self._title} (Object, Threads, WCET(1), '
        desc += f'WCET(1) * Thread Count) Table'
        desc += f'\nobject | threads | c(1) | c(1) * threads'
        desc += '\n' + '-' * 70
        for obj, threads in thrd_tbl.items():
            wcet_one = wcet_tbl[obj](1)
            desc += '\n'
            desc += f'{obj:>6} | {threads:>7} | {wcet_one:>4} | '
            desc += f'{wcet_one * threads:>4}'
        logging.info(desc)
        
class ExactColo(TaskWCET):
    def sec_span(self, sec, m=None):
        pfx=self._title
        if m:
            self.cores = m
        if not m and not self.cores:
            raise Exception('Cores are unset')
        
        # Parallel Setup
        manager = multiprocessing.Manager()
        self._queue = manager.Queue(PARALLEL_CHUNK)

        # Collect the objects
        thread_map = sec.threads_by_object()

        # Create the base iterators thanks to idiot
        itbyobj = {}
        total = 1
        for object, threads in thread_map.items():
            iterator = idiot(threads, m)
            total *= iterator.length()
            itbyobj[object] = iterator

        cross = itertools.product(*itbyobj.values())
        cross, copy = itertools.tee(cross)
        procs = min(os.cpu_count(), total)
        step = math.ceil(total / procs)

        # The cross product of the idiot iterators is the complete set
        # of possible schedules.  
        data = []
        for p in range(procs):
            start = p * step
            stop = (p + 1) * step
            cross, copy = itertools.tee(cross)
            iterables = itertools.islice(copy, start, stop)
            data.append([iterables, sec, self._queue])

        self.desc_tbl(sec.threads_by_object(), sec.wcet_by_object())            

        # Parallel processing pool
        logging.info(f'{pfx} processes:{procs} schedules:{total}')
        with multiprocessing.Pool(processes=procs) as pool:
            results = pool.map_async(self.sec_span_part, data)
            title=f'{self._title}'
            with alive_progress.alive_bar(total, title=title,
              length=20,bar='filling', spinner='dots_waves') as bar:
                for i in range(total):
                    finished = self._queue.get()
                    bar(finished)
                    # alive_progress.alive_bar doesn't do simple math
                    total = total - finished
                    if total <= 0:
                        break
            makespans = results.get()
            makespan = None
            for span, descr in makespans:
                if not span:
                    continue
                if not makespan or span < makespan:
                    makespan = span
                    desc = descr
        del self._queue
        print(f'{pfx} Minimum makespan schedule:')
        print(desc)
        return makespan
        

    def sec_span_part(self, *args):
        iterator, sec, q = list(*args)
        step = PARALLEL_CHUNK

        count = 0
        min_makespan = None
        descrs = []
        for a in iterator:
            scheds = [0] * self.cores
            scheds_descr = [''] * self.cores
            for obj, omap in zip(sec.objects, a):
                for idx in range(self.cores):
                    name = obj.name
                    threads = omap[idx]
                    wcet = obj.wcet_fn(threads)
                    scheds[idx] += wcet
                    if threads == 0:
                        continue
                    scheds_descr[idx] += \
                        f'{name:>2}({threads:>2}):{wcet:>3} '
            # core schedules have been bounded

            # Does this new schedule have a shorter makespan?
            sched_span = max(scheds)
            if not min_makespan or sched_span < min_makespan:
                # Yes! New minimum
                min_makespan = sched_span
                # Create the description for debugging
                descrs = []
                for i in range(self.cores):
                    descrs.append(f'S{i} | ' + scheds_descr[i]
                                  + f'≤ {scheds[i]}')

            # Increase the number of schedules explored.
            count += 1
            if count == step:
                # Batch update
                q.put(count)
                count = 0
        # Catch any missing schedule updates
        if count != 0:
            q.put(count)
        # Let the queue go
        return min_makespan, '\n'.join(descrs)


    def desc_tbl(self, thrd_tbl, wcet_tbl):
        # Informational table
        maxthread = max(thrd_tbl.values())
        desc = f'{self._title} Object/Thread/WCET Table:\nobject | threads | '
        for i in range(1, maxthread + 1):
            desc += f'c({i}) '
        desc += '\n' + '-' * 70
        for obj, threads in thrd_tbl.items():
            desc += '\n'
            desc += f'{obj:>6} | {threads:>7} | '
            for i in range(1,threads + 1):
                desc += f'{wcet_tbl[obj](i):>4} '
        logging.info(desc)

