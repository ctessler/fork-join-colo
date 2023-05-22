__all__ = [ ]

import matplotlib.colors as colors
import math

#
# Algorithm parameter and keyname definitions 
#
def get_label(algname):
    '''
    Returns the label to use in the graphs given the name of the
    algorithm found in the task set (tasks.csv)
    '''
    labels = {
        'ExactColo'   : 'ExactColo',
        'ExactNoColo' : 'ExactNoColo',
        '3-Parm'      : '3-Parm',
        '3-Parm-HD'   : '3-Parm-HD',
        '2-Gram'      : 'Graham',
        'DAG-m'       : 'DAG-m',
        'DAG-LP'      : 'DAG-LP',
        'DAG-GB'      : 'DAG-GB',
    }

    if not algname in labels:
        raise Exception(f'Unknown algorithm name {algname}')

    return labels[algname]

def algs_approx():
    '''
    Returns the list of approximation algorithms
    '''
    return ['3-Parm', '3-Parm-HD', '2-Gram']

def algs_exact():
    '''
    Returns the list of exact algorithms
    '''
    return ['DAG-m', 'ExactColo', 'ExactNoColo']

def algs_dag():
    '''
    Returns the list of DAG algorithms
    '''
    return ['DAG-LP', 'DAG-GB']

def algs_ordered(skip_exact=False, skip_dag=False):
    '''
    Returns the list of all algorithms, ordered.

    skip_exact : do not include exact algorithms
    skip_dag : do not include dag algorithms
    '''
    rval = algs_approx()
    if not skip_dag:
        rval = rval + algs_dag()
    if not skip_exact:
        rval = rval + algs_exact()

    return rval

def task_key_reuse():
    '''
    Returns the label for the cache reuse factor
    '''
    return 'CacheReuseFactor'


def parm_pairs(parm):
    '''
    Helper for the pairs of parms
    '''
    pairs = []
    for alg in algs_ordered():
        pairs.append((alg, alg + parm))
    return pairs

def pair_dict(pairs):
    '''
    Helper for the dict of parms
    '''
    d = {}
    for (k, v) in pairs:
        d[k] =v
    return d

def key_cores_pairs():
    '''
    Returns an ordered list of core keys for algorithms
    '''
    return parm_pairs('-Cores')

def key_cores_dict():
    '''
    Returns a dictionary of algorithm to core keys
    '''
    return pair_dict(key_cores_pairs())

def key_cores(alg):
    '''
    Returns the cores key for an algorithm
    '''
    return key_cores_dict()[alg]

def key_sched_pairs():
    '''
    Returns an ordered list of schedulable keys for algorithms
    '''
    return parm_pairs('-Sched')

def key_sched_dict():
    '''
    Returns a diction of algorithm to schedulable keys
    '''
    return pair_dict(key_sched_pairs())

def key_sched(alg):
    '''
    Returns the schedulability key for an algorithm
    '''
    return key_sched_dict()[alg]

def key_seconds_pairs():
    '''
    Returns an ordered list of second keys for algorithms
    '''
    return parm_pairs('-Seconds')

def key_seconds_dict():
    '''
    Returns a diction of algorithm to seconds keys
    '''
    return pair_dict(key_seconds_pairs())

def key_seconds(alg):
    '''
    Returns the seconds key for an algorithm
    '''
    return key_seconds_dict()[alg]

def key_WCET_pairs():
    '''
    Returns an ordered list of WCET keys for algorithms
    '''
    return parm_pairs('-WCET')

def key_WCET_dict():
    '''
    Returns a diction of algorithm to WCET keys
    '''
    return pair_dict(key_WCET_pairs())

def key_WCET(alg):
    '''
    Returns the WCET key for an algorithm
    '''
    return key_WCET_dict()[alg]

#
# Aesthetic definitions
#
def get_color_pairs():
    '''
    Returns an ordered list of pairs of algorithms and colors

    ( (alg1, color1), (alg2, color2), ... )
    '''
    color_list = ((57, 106, 177), # blue
                  (218, 124, 48), # orange
                  (62, 150, 81),  # green
                  (107, 75, 154), # purple
                  (146, 36, 40),  # dark red
                  (148, 139, 61), # gold
                  (204, 37, 41),  # red
                  (83, 81, 84)    # dark gray
                  )
    hlist = []
    for (r, g, b) in color_list:
        hlist.append(f'#{r:x}{g:x}{b:x}')

    pair_list = zip(algs_ordered(), hlist)
    return list(pair_list)

def get_color_dict():
    '''
    Returns a dictionary of algorithm to color

    { alg1 : color1, alg2 : color2, ... }
    '''
    return pair_dict(get_color_pairs())

def get_color(alg, bar=False):
    '''
    Returns the color of an algorithm
    '''
    if bar:
        return colors.TABLEAU_COLORS['tab:gray']
    
    return get_color_dict()[alg]

def get_line_pairs():
    '''
    Returns an ordered list of pairs of algorithms and line styles
    '''
    line_styles = ('solid', #3-Parm
                   'solid', #3-Parm-HD
                   'solid', #2-Gram
                   (0, (1, 2)),  #DAG-m
                   (0, (2, 2)),  #DAG-LP
                   (0, (3, 2)),   #DAG-GB
                   (0, (9, 2)),       #ExactColo 
                   (0, (7, 1, 1, 1)) #ExactNoColo
                   )

    return list(zip(algs_ordered(), line_styles))

def get_line_dict():
    '''
    Returns a dictionary of algorithms to line styles
    '''
    return pair_dict(get_line_pairs())

def get_line(alg):
    '''
    Returns the line style of an algorithm
    '''
    return get_line_dict()[alg]

def get_marker_pairs():
    '''
    Returns an ordered list of pairs of algorithms and marker styles
    '''
    markers = ('o', 'X', 'P', 'None', 'None', '|', 2, 3)
    markers = ('o', 'X', 'P', 'None', 'None', 'None', 'None', 'None')
    
    return list(zip(algs_ordered(), markers))

def get_marker_dict():
    '''
    Returns a dictionary of algorithm to marker style
    '''
    return pair_dict(get_marker_pairs())

def get_marker(alg):
    '''
    Returns a marker style for an algorithm
    '''
    return get_marker_dict()[alg]


def get_markerfacecolor_pairs():
    '''
    Returns an order list of pairs of algorithms and colors
    '''
    color_list = ((57, 106, 177), # blue
                  (218, 124, 48), # orange
                  (62, 150, 81),  # green
                  (107, 75, 154), # purple
                  (146, 36, 40),  # dark red
                  (148, 139, 61), # gold
                  (204, 37, 41),  # red
                  (83, 81, 84)   # dark gray
                  )
    hlist = []
    for (r, g, b) in color_list:
        r = min(r + 64, 255)
        g = min(g + 64, 255)
        b = min(b + 64, 255)
        hlist.append(f'#{r:x}{g:x}{b:x}')


    pair_list = zip(algs_ordered(), hlist)
    return list(pair_list)

def get_markerfacecolor_dict():
    '''
    Returns a dictionary of algorithm to marker style
    '''
    return pair_dict(get_markerfacecolor_pairs())

def get_markerfacecolor(alg):
    '''
    Returns a marker style for an algorithm
    '''
    return get_markerfacecolor_dict()[alg]

def get_markersize_pairs():
    '''
    Returns an order list of pairs of algorithms and sizes
    '''
    sizes = [10] * len(algs_ordered())
    pair_list = zip(algs_ordered(), sizes)
    return list(pair_list)

def get_markersize_dict():
    '''
    Returns a dictionary of algorithm to marker style
    '''
    return pair_dict(get_markersize_pairs())

def get_markersize(alg):
    '''
    Returns a marker style for an algorithm
    '''
    return get_markersize_dict()[alg]

def get_markevery_pairs():
    '''
    Returns an ordered list of pairs of algorithms and markevery
    distances
    '''
    primes = [1, 2]
    every = []
    for i in range(len(algs_ordered())):
        idx = i % len(primes)
        every.append(primes[idx])

    return list(zip(algs_ordered(), every))

def get_markevery_dict():
    '''
    Returns a dictionary of algorithm to markevery distance
    '''
    return pair_dict(get_markevery_pairs())

def get_markevery(alg, rangeobj=None):
    '''
    Returns a markevery for an algorithm
    '''
    factor = 1
    if rangeobj:
        factor = math.ceil(max(rangeobj) / 5)

    base = 1
    if False: # Put this back if the offsets are preferable.
        base = get_markevery_dict()[alg]
    
    return base * factor

def axis_fontsize():
    '''
    Returns the fontsize of the axis
    '''
    return 14


