__all__ = ['least_penalty']

import dagot.MinCores
from dagot.Shared import *
import logging


def debug_lp_pair_string_no_ext(task, pairs):
    firstdone = False
    str = '['
    for p in pairs:
        a, b = p
        if firstdone:
            str += ', '
        firstdone = True
        str += f'<{a.name},{b.name}> '
    str += ']'
    return str



def debug_lp_pair_string(task, pairs):
    firstdone = False
    str = '['
    for p in pairs:
        a, b = p
        if firstdone:
            str += ', '
        firstdone = True
        ext = task.colo_critical_path_extension(a, b)
        str += f'<{a.name},{b.name}>+{ext}'
    str += ']'
    return str
    
    
def least_penalty(task=None):
    '''
    Calculates the minimum number of cores for the task after
    collapsing candidates based on the least penalty heuristic

    Note, writing the task back to disk will alter the structure
    of the task file. Do *not* write this task back to disk if
    the original structure has value, it will be erased.
    '''

    pairs = task.candidate_pairs()
    logging.debug('Unordered pairs: ' + debug_lp_pair_string_no_ext(task, pairs))

    ordered = sorted(pairs,
                     key=lambda p: task.colo_critical_path_extension(*p))
    logging.debug('Ordered pairs: ' + debug_lp_pair_string(task, ordered))

    return beneficial_colocations(task, ordered)
        
    
