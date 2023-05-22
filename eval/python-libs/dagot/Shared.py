__all__ = [ 'beneficial_colocations' ]

import dagot.MinCores
import logging

def beneficial_colocations(task, ordered):
    '''
    task - the task where nodes will be colocated.
    order - the set of nodes to colocate (only if they would be
    beneficial)

    the task is modified and the number of cores returned
    '''

    colocations = 0
    for pair in ordered:
        a, b = pair

        # a or b may have been co-located, and therefor removed
        # move on to next pair if one does not exist in the task
        if not task.contains_node(a):
            logging.debug(f'{a.name} has been removed via co-location')
            continue
        if not task.contains_node(b):
            logging.debug(f'{b.name} has been removed via co-location')        
            continue
        
        ext = task.colo_critical_path_extension(a, b)
        if ext == None:
            continue

        newcpath = task.critical_path_length() + ext
        if newcpath >= task.deadline:
            logging.debug(f'Colocating <{a.name},{b.name}> '
                          f'would extend the critical path by {ext} '
                          f'to {newcpath} beyond the deadline '
                          f'{task.deadline}')
            logging.debug(f'Skipping colocation of <{a.name},{b.name}>')
            continue

        workdiff = task.colo_work_reduction(pair[0], pair[1])

        # Ensure colocation does not create an unschedulable task
        sched = dagot.MinCores.min_cores_sched_est(
            task.work() - workdiff, newcpath, task.deadline)
        if not sched:
            logging.debug(f'Colocating <{a.name},{b.name}> would '
                          f'create an unschedulable task, skipping')
            continue

        # Ensure the colocation does not increase the number of cores
        precores = dagot.MinCores.min_cores(task)
        postcores = dagot.MinCores.min_cores_est(
            task.work() - workdiff, newcpath, task.deadline)
        if postcores > precores:
            logging.debug(f'Colocating <{a.name},{b.name}> would '
                          f'increase the number of cores from '
                          f'{precores} to {postcores} '
                          f'skipping colocation')
            continue

        colocations += 1
        task.colocate(a, b)
        cores = dagot.MinCores.min_cores(task)

        if newcpath != task.critical_path_length():
            logging.warning(f'Calculated extension {newcpath} does '
                            f'not match actual '
                            f'{task.critical_path_length()}')
            raise Exception('Incorrect extension calculation')
        
        logging.debug(f'Colocating <{a.name},{b.name}> '
                      f'extending the critical path by {ext} '
                      f'requires cores {cores}')

    sched = dagot.MinCores.min_cores_sched(task)
    if not sched:
        logging.debug(f'Task is not schedulable')
        if colocations > 0:
            logging.debug(f'Incorrect application of colocation')
            raise Exception('Incorrect colocation behavior')
        return 0
        
    return dagot.MinCores.min_cores(task)
    
