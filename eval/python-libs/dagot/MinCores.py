from colo.ForkJoinTask import ForkJoinTask
import math

def min_cores_sched(task):
    '''
    Determines if a task is suitable for minimum cores calculation
    '''
    cpath = task.critical_path_length()
    work = task.work()
    deadline = task.deadline

    return min_cores_sched_est(work, cpath, deadline)
    

def min_cores(task):
    '''
    Calculates the minimum number of cores when a ForkJoinTask is
    treated as a DAG-OT task

    '''
    if not isinstance(task, ForkJoinTask):
        raise Exception('task must be an instance of a ForkJoinTask')

    cplength = task.critical_path_length()
    workload = task.work()
    deadline = task.deadline

    return min_cores_est(workload, cplength, deadline)

def min_cores_est(work, cpath, deadline):
    '''
    Calculates the minimum number of cores for a hypothetical
    ForkJoinTask

             { workload - critical path length }
    m = ceil { ------------------------------- }
             { deadline - critical path length }
    '''

    cores = math.ceil((work - cpath) / (deadline - cpath))

    return cores
    
    
def min_cores_sched_est(work, cpath, deadline):
    '''
    Determines if a hypothetical task is suitable for minimum cores
    calculation 

    Returns True if this task *could* be assigned a minimum number of
    cores, returns false otherwise (i.e. unschedulable)
    '''

    if work <= cpath:
        return False

    if deadline <= cpath:
        return False

    return True
