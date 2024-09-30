all = ['idiot',
       'Timer']

import itertools
import math

class idiot(itertools.combinations):
    '''
    An iterator for the Distribution Of Identical Objects To Distinct
    Bins (DOIOTDB). For some reason, that is beyond my ability to
    understand, the acronym the class name uses doesn't quite match.
    '''
    def __init__(self, num_objects, bins):
        self._nobjects = num_objects
        self._nbins = bins
        
    def __new__(cls, num_objects, bins):
        return super().__new__(
            cls, range(1, num_objects + bins), bins - 1)

    def __next__(self):
        last_bar = 0
        bin_count = []
        for index in super().__next__():
            bin_count.append(index - (last_bar + 1))
            last_bar = index
        bin_count.append(self._nobjects - sum(bin_count))
        return bin_count

    def length(self):
        return math.comb(self._nobjects + self._nbins - 1,
                         self._nbins - 1)


def prev_result(ident, task, cores_min, cores_max):
    cores = task.get_result(ident + '-Cores')
    wcet = task.get_result(ident + '-WCET')

    if not cores or not wcet:
        # No previous result
        return [False, cores_min]

    cores = int(cores)
    wcet = int(wcet)

    if wcet <= task.deadline:
        # Previous result covers this one
        return [True, cores_min,
                f'Previous success wcet:{wcet} cores:{cores}',
                f'Remove existing results if recalculation is desired']

    # Previous result was a failure

    if cores >= cores_max:
        # Won't succeed without adding cores
        return [True, cores_min,
                f'Previous failure wcet:{wcet} cores:{cores}',
                f'Increase --cores-max to calculate']

    # Start with a greater value for cores_min
    cores_min = cores + 1
    return [False, cores_min,
            f'Previous failure wcet:{wcet} cores:{cores}',
            f'Starting with {cores_min} cores']
    

import time
class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        if self._start_time is not None:
            raise Exception("Timer is already running")
        self._start_time = time.perf_counter()
        self._elapsed_time = None

    def stop(self):
        if self._start_time is None:
            raise Exception("Timer is not running")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        self._elapsed_time = elapsed_time
        return elapsed_time

    @property
    def elapsed(self):
        return self._elapsed_time

import colo
import json
import logging
import os
def prev_check(ident, task, cores_min, cores_max, force=False):
    '''
    Returns false if the task includes a previous result and is not
    forced to over-write it.
    '''
    stop, cores_min, *msgs = \
        colo.Helpers.prev_result(ident, task, cores_min, cores_max)
    if stop and not force:
        for m in msgs:
            logging.warning(m)
        return False
    for m in msgs:
        logging.info(m)
    return True

import signal
def core_alloc(ident, solver_class, task_path, cores_min, cores_max,
               force=False):
    path = os.path.normpath(task_path)
    if not os.path.isfile(path):
        raise Exception(f'Task file: {path} does not exist')

    with open(path, 'r') as fp:
        task = json.load(fp, cls=colo.ForkJoinTaskDecoder)

    if not prev_check(ident, task, cores_min, cores_max, force):
        return -1
        
    timer = Timer()
    timer.start()
    log_pfx = f'{ident}(Task:{task.name}) ⇨'
    min_cores = None
    wcet = None
    logging.info(f'{log_pfx} Running for [{cores_min}, {cores_max}] cores')
    for m in range(cores_min, cores_max + 1):
        solver = solver_class(task)
        try:
            wcet = solver.wcet(m)
        except KeyboardInterrupt as k:
            # Interrupted
            wcet = None
            break
        if wcet <= task.deadline:
            logging.info(f'{log_pfx} {m}-core WCET {wcet} ≤ '
                         f'{task.deadline} deadline, done exploring.')
            min_cores = m
            break
        logging.info(f'{log_pfx} {m}-core WCET {wcet} > '
                     f'{task.deadline} deadline, continuing.')
    timer.stop()
    terminated=False
    if not wcet:
        logging.warning(f'⚠ {log_pfx} interrupted')
        min_cores = None
        terminated = True
    
    if not min_cores:
        logging.warning(f'⚠ {log_pfx} could not meet its deadline '
                        f'with {cores_max} cores')
        min_cores = cores_max

    logging.info(f'{log_pfx} took {timer.elapsed:0.3} seconds')
    task.set_result(ident + '-Cores', min_cores)
    task.set_result(ident + '-WCET', wcet)
    task.set_result(ident + '-Seconds', timer.elapsed)
    task.set_result(ident + '-Terminated', terminated)
    logging.info(f'{log_pfx} Writing result with task to {path}')
    with open(path, 'w') as fp:
        json.dump(task, fp, cls=colo.ForkJoinTaskEncoder, indent=4)
    return 0

import multiprocessing
def bounded_core_alloc(ident, solver_class, task_path, cores_min,
                       cores_max, force=False, timeout=600):

    logging.error(f'⚠ Limited timing is incorrectly implemented, aborting!')
    return -1
    
    path = os.path.normpath(task_path)
    if not os.path.isfile(path):
        raise Exception(f'Task file: {path} does not exist')

    with open(path, 'r') as fp:
        task = json.load(fp, cls=colo.ForkJoinTaskDecoder)

    if not prev_check(ident, task, cores_min, cores_max, force):
        return -1


    
    allocp = multiprocessing.Process(target=core_alloc,
        args=(ident, solver_class, task_path, cores_min, cores_max,
              force))

    log_pfx = f'{ident}(Task:{task.name}) ⇨'
    allocp.start()
    allocp.join(timeout=timeout)

    if allocp.exitcode is not None:
        logging.info(f'{log_pfx} satisfied time allotment')
        return allocp.exitcode

    print(f'{os.getpid()} is Killing {allocp.pid}')
    while allocp.is_alive():
        os.kill(allocp.pid, signal.SIGINT)
        #allocp.terminate()

    logging.warning(f'\n⚠ {log_pfx} terminated for exceeded time '
                    f'allotment of {timeout} seconds')
    return 0
        
        
    
    
