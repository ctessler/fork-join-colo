__all__ = ['greatest_benefit']

import dagot.MinCores
from dagot.Shared import beneficial_colocations
import logging

def _gb_sorter(pair):
    left = pair[0]
    right = pair[1]
    wcetfn = left.object.wcet_fn
    total = left.bound() + right.bound()
    combined = wcetfn(left.threads + right.threads)
    reduction = total - combined

    logging.debug(f'Combining nodes {left.name} and {right.name} '
                  f'saves {reduction}')

    return reduction

def debug_pair_string(pairs):
    firstdone = False
    str = '['
    for p in pairs:
        if firstdone:
            str += ', '
        firstdone = True
        str += f'<{p[0].name},{p[1].name}>'
    str += ']'
    return str
    
    
def greatest_benefit(task=None):
    '''
    Calculates the minimum number of cores for the task after
    collapsing candidates based on the greatest benefit heuristic

    Note, writing the task back to disk will alter the structure
    of the task file. Do *not* write this task back to disk if
    the original structure has value, it will be erased.
    '''

    pairs = task.candidate_pairs()
    logging.debug('Unordered pairs: ' + debug_pair_string(pairs))

    ordered = sorted(pairs, key=_gb_sorter, reverse=True)
    logging.debug('Ordered pairs: ' + debug_pair_string(ordered))

    return beneficial_colocations(task, ordered)
