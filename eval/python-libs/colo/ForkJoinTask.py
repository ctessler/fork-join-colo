__all__= ['ForkJoinObject',
          'ForkJoinNode',
          'ForkJoinTask',
          'ForkJoinTaskSet',
          'ParallelSection',
          'WCET',
          'ForkJoinObjectEncoder',
          'ForkJoinTaskEncoder',
          'ForkJoinObjectDecoder',
          'ForkJoinTaskDecoder',
          'ForkJoinTaskSetEncoder'
          ]

import json
import logging

class ForkJoinObject:
    '''
    Represents an executable object
    '''
    instance = 0

    def __init__(self, name_str=None, wcet_func=None):
        self.name = ForkJoinObject.instance
        ForkJoinObject.instance += 1

        if name_str:
            self.name = name_str
        if wcet_func:
            self.wcet_fn = wcet_func

    def __eq__(self, other):
        return self._name == other._name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @name.deleter
    def name(self):
        del self._name

    @property
    def wcet_fn(self):
        return self._wcet_fn

    @wcet_fn.setter
    def wcet_fn(self, value):
        if not callable(value):
            raise Exception('wcet_fn must be callable')
        self._wcet_fn = value

    @wcet_fn.deleter
    def wcet(self):
        del self._wcet_fn

    def encode(self):
        descr = {
            'name' : self._name,
            'base' : self._wcet_fn.base,
            'incr' : self._wcet_fn.incr
        }
        return descr


class ForkJoinNode:
    '''
    Represents a node within a Fork-Join task
    '''
    instance = 1

    def __init__(self, name=None, object=None,
                 threads=1):
        self._name = ForkJoinNode.instance
        ForkJoinNode.instance += 1

        self._on_cpath = False
        self._threads = threads
        if not name is None:
            self._name = name
        if not object is None:
            if not isinstance(object, ForkJoinObject):
                raise Exception('value must be a ForkJoinObject')
            self._object = object

    def bound(self):
        return self.object.wcet_fn(self.threads)

    @property
    def name(self):
        '''Gets the name of the node'''
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @name.deleter
    def name(self):
        del self._name

    @property
    def object(self):
        '''Gets the object of the node'''
        if not isinstance(self._object, ForkJoinObject):
            raise Exception('value must be a ForkJoinObject')
        return self._object

    @object.setter
    def object(self, value):
        if not isinstance(value, ForkJoinObject):
            raise Exception('value must be a ForkJoinObject')
        self._object = value

    @object.deleter
    def object(self):
        del self._object

    @property
    def threads(self):
        '''Gets the threads of the node'''
        return self._threads

    @threads.setter
    def threads(self, value):
        self._threads = value

    @threads.deleter
    def threads(self):
        self._threads = 0

    @property
    def critical(self):
        '''Gets the node's participation on the critical path'''
        return self._on_cpath

    @critical.setter
    def critical(self, value):
        if not (type(value) is bool):
            raise Exception('critical path must be True or False')
        self._on_cpath = value

    @critical.deleter
    def critical(self):
        self._on_cpath = False

    def __str__(self):
        s = f"<{self.name}:c"
        s += f"({self._threads})"
        s += f"={self.bound()}>"
        return s


class WCET:
    '''
    Represents a WCET function that accepts a number of threads
    c(n) = base + incremental * (n - 1)


    c = WCET(base=10, incr=2)
    print(c(2))        # prints 14
    print(c.bound(20)) # prints 20

    '''
    def __init__(self, b=None, i=None):
        self.base = 0
        self.incr = 0

        if b:
            self.base = b
        if i:
            self.incr = i

    def __call__(self, threads):
        '''
        An alternative method to get the WCET for threads

        Equivalent to bound(threads)
        '''
        return self.bound(threads)

    def bound(self, threads):
        '''
        Returns the WCET of <threads>
        '''
        if threads == 0:
            return 0
        b = self._base
        g = self._incr
        return b + (threads - 1) * g

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        self._base = value

    @base.deleter
    def base(self):
        self._base = 0

    @property
    def incr(self):
        return self._incr

    @incr.setter
    def incr(self, value):
        self._incr = value

    @incr.deleter
    def incr(self):
        self._incr = 0


class ForkJoinTask:
    instance = 0
    def __init__(self, name=None):
        if not name:
            name = str(ForkJoinTask.instance)
            ForkJoinTask.instance += 1

        self._data = {
            'sections'    : [], # Parallel Sections
            'ser_nodes'   : [], # Ordered sequential nodes (fork/join)
            'objects'     : [], # Objects
            'name'        : name,
            'deadline'    : None,
            'results'     : {}
        }

    def infeasible(self):
        '''Determines if this task is infeasible'''
        if not self.deadline:
            logging.debug(f'Task:{self.name} has no deadline')
            return True
        if not self.objects or len(self.objects) == 0:
            logging.debug(f'Task:{self.name} has no objects')
            return True
        total = sum(sec.min_wcet() for sec in self.sections)
        total += self.serial_wcet
        if total > self.deadline:
            logging.debug(f'Task:{self.name} total demand {total} '
                          f'> deadline {self.deadline}')
            return True
        return False

    def cache_reuse_factor(self):
        '''
        Returns the cache reuse factor of the task
        '''
        cost_wo_colo = 0
        cost_wi_colo = 0

        for node in self.serial_nodes:
            # Serial nodes will have exactly 1 thread
            cost_wo_colo += node.bound()
            cost_wi_colo += node.bound()

        for sec in self.sections:
            cost_wo_colo += sec.max_demand()
            cost_wi_colo += sec.min_demand()

        reuse_factor = 1 - (cost_wi_colo / cost_wo_colo)
        return reuse_factor


    def avg_cache_availability(self):
        '''
        Returns the average cache availability which is defined in
        terms of the cache available for each node CAN and the total
        number of nodes N:

           Sum of CAN for all N parallel objects
           -----------------------------------
                           N

        Note: Sequential (fork/join) nodes cannot contribute to
        availability
        '''
        raise Exception('Deprecated')
        obj_count = 0
        ca_total = 0
        for node in self.serial_nodes:
            # Serial nodes have no contribution but one object
            obj_count += 1

        for sec in self.sections:
            ca_table = sec.cache_availability_by_object()
            for obj, avail in ca_table.items():
                ca_total += avail
                obj_count += 1

        avg = ca_total / obj_count
        return avg


    @property
    def serial_wcet(self):
        '''
        Returns the combined WCET of the serial (fork and join) nodes
        '''
        total = sum(node.bound() for node in self.serial_nodes)
        return total

    @property
    def name(self):
        return self._data['name']
    @name.setter
    def name(self, value):
        self._data['name'] = value
    @name.deleter
    def name(self, value):
        self._data['name'] = None

    @property
    def sections(self):
        return self._data['sections']

    @sections.setter
    def sections(self, seclist):
        self._data['sections'] = seclist

    @sections.deleter
    def sections(self):
        del self._data['sections']

    def add_section(self, sec):
        error_msg = 'Task already contains nody by name '
        psec = None # section already [P]resent in task
        for psec in self.sections:
            for node in sec.nodes:
                name = node.name
                found = psec.node_by_name(name)
                if found:
                    raise Exception(error_msg + str(name))

        self._data['sections'].append(sec)

    @property
    def objects(self):
        return self._data['objects']

    @objects.setter
    def objects(self, objlist):
        self._data['objects'] = objlist

    @objects.deleter
    def objects(self):
        del self._data['objects']

    @property
    def serial_nodes(self):
        return self._data['ser_nodes']

    @serial_nodes.setter
    def serial_nodes(self, nodelist):
        self._data['ser_nodes'] = nodelist

    @serial_nodes.deleter
    def serial_nodes(self):
        del self._data['ser_nodes']

    def add_serial_node(self, node):
        self._data['ser_nodes'].append(node)

    @property
    def deadline(self):
        return self._data['deadline']

    @deadline.setter
    def deadline(self, value):
        self._data['deadline'] = value

    @deadline.deleter
    def deadline(self):
        self._data['deadline'] = None

    def set_result(self, tag, value):
        '''
        Sets a result, like the number of cores

        task.set_result('exact-min-cores', 5)
        '''
        self._data['results'][tag] = value

    def get_result(self, tag):
        '''
        Gets a previously set result
        '''
        if not tag in self._data['results']:
            return None

        return self._data['results'][tag]

    def get_object(self, oname):
        '''
        Finds the object (by name) of all the objects in the task

        Returns None when the object is not included
        '''
        for obj in self._data['objects']:
            if obj.name != oname:
                continue
            return obj
        return None

    def total_threads(self):
        '''
        Returns the sum of all threads of all nodes in the task
        '''
        threads=0
        for node in self.serial_nodes:
            threads += node.threads

        for sec in self.sections:
            threads += sec.total_threads()

        return threads


    def threads_by_object(self):
        '''
        Returns a hash of object name : thread count
        For all objects in the task.

        object | threads
        -------+--------
           a1  |  n1
           a2  |  n2
        '''
        otmap = {}
        for node in self.serial_nodes:
            oname = node.object.name
            if not oname in otmap:
                otmap[oname] = node.threads
            else:
                otmap[oname] += node.threads

        for sec in self.sections:
            submap = sec.threads_by_object()
            for oname, threads in submap.items():
                if not oname in otmap:
                    otmap[oname] = threads
                else:
                    otmap[oname] += threads
        return otmap

    def demand(self, min=False):
        '''
        Gets the total demand for the task

        Note: demand is with respect to *objects* not nodes

        When min is True, assume all objects that can be co-located
        are. When min is False, assume *none* of the objects that can
        be co-located are.
        '''
        # Object to Thread Count Map
        otmap = self.threads_by_object()
        demand = 0
        for oname, threads in otmap.items():
            object = self.get_object(oname)
            if min:
                demand += object.wcet_fn(threads)
            else:
                demand += object.wcet_fn(1) * threads
        return demand

    def critical_path(self):
        '''
        Gets the critical path of the task as a list of nodes
        '''
        # The critical path is the concatenation of
        # serial node
        #     -> maximum node of parallel segment
        #     -> serial node ...
        #     ...
        #     -> maximum node of final parallel segment
        #     -> terminal node

        # Reset critical path participation
        for node in self.serial_nodes:
            node.critical = False
        for sec in self.sections:
            for node in sec.nodes:
                node.critical = False

        path = []
        for idx in range(len(self.serial_nodes) - 1):
            fjnode = self.serial_nodes[idx]
            secnode = self.sections[idx].max_wcet_node()

            fjnode.critical = True
            secnode.critical = True

            path.append(fjnode)
            path.append(secnode)

        lastnode = self.serial_nodes[-1]
        lastnode.critical = True
        path.append(lastnode)

        return path

    def critical_path_length(self):
        '''
        Returns the critical path length through the task
        '''
        cpath = self.critical_path()
        length = sum(node.bound() for node in cpath)
        return length

    def work(self):
        '''
        Returns the total demand of all nodes within the task
        This differs from demand() in that it is with respect to
        *nodes* and not objects. Thus the number of threads assigned
        to each node is taken into account when calculating its demand
        '''
        C = 0
        for n in self.serial_nodes:
            C += n.bound()
        for sec in self.sections:
            for n in sec.nodes:
                C += n.bound()

        return C

    def max_benefit_value(self):
        '''
        Returns the maximum benefit of collapsing any pair of nodes in
        the task. The reduction in workload is returned, the pair of
        nodes is not stored.
        '''
        maxb = 0
        for sec in self.sections:
            curb = sec.max_benefit_value()
            maxb = max(curb, maxb)
        return maxb

    def max_benefit_collapse(self):
        '''
        Performs the collapse of the maximum benefit pair in the
        parallel section

        Returns true upon success
        '''
        maxb = self.max_benefit_value()
        if maxb == 0:
            return False

        for sec in self.sections:
            curb = sec.max_benefit_value()
            if curb != maxb:
                continue
            sec.max_benefit_collapse()
        return True

    def candidate_pairs(self):
        '''
        Returns all candidate pairs in no order

           +- pair -+
           |        |
        [ [node, node], [node, node], [node, node] ... ]
        '''
        pairs = []
        for sec in self.sections:
            pairs = pairs + sec.candidate_pairs()
        return pairs

    def contains_node(self, n):
        '''
        Determines if the node is contained in the task

        returns True if the node is present
        '''
        for sec in self.sections:
            node = sec.node_by_name(n.name)
            if node:
                return True
        return False

    def colo_critical_path_extension(self, a, b):
        '''
        Assuming nodes can be colocated, return the
        extension in the critical path length the colocation would
        yield.

        Raises exceptions upon incorrect input
        '''
        # Updates each node with the critical path tag
        path = self.critical_path()
        for sec in self.sections:
            left  = sec.node_by_name(a.name)
            right = sec.node_by_name(b.name)
            if left == None:
                continue
            return sec.colo_cp_ext(a, b)

    def colo_work_reduction(self, a, b):
        '''
        Assuming the nodes can be colocated, return the reduction
        in the total workload colocation would yield.

        Raises an exception upon incorrect input
        '''
        for sec in self.sections:
            left = sec.node_by_name(a.name)
            right = sec.node_by_name(b.name)
            if left == None:
                continue
            return sec.colo_work_reduction(left, right)

    def colocate(self, a, b):
        '''
        Colocates nodes a and b
        '''
        for sec in self.sections:
            left = sec.node_by_name(a.name)
            right = sec.node_by_name(b.name)
            if left == None:
                continue
            sec.colocate(left, right)
            return


class ForkJoinTaskSet:
    instance = 0

    def __init__(self, name=None):
        if not name:
            name = ForkJoinTaskSet.instance
        ForkJoinTaskSet.instance += 1
        self._data = {
            'tasks': [],
            'name' : name
        }

    @property
    def name(self):
        return self._data['name']

    @name.setter
    def name(self, value):
        self._data['name'] = value

    @name.deleter
    def name(self, value):
        del self._data['name']

    @property
    def tasks(self):
        return self._data['tasks']

    @tasks.setter
    def tasks(self, value):
        self._data['tasks'] = value

    @tasks.deleter
    def tasks(self):
        self._data['tasks'] = []



class ParallelSection:
    '''
    Represents an individual parallel section

    Contains ForkJoinNode s
    '''
    def __init__(self, nodes=None):
        if nodes and not isinstance(nodes, list):
            raise Exception('nodes must be a list of ForkJoinNodes')
        # Pair of L 'parallel' nodes
        self._data = {
            'nodes' : []
        }
        if nodes:
            self.nodes = nodes

    def min_wcet(self):
        '''
        Returns the minimum WCET for this parallel section,
        which is equivalent to the node with the greatest WCET value
        '''
        max_node = \
            max(self.nodes, key=lambda node: node.bound())
        return max_node.bound()

    def max_demand(self):
        '''
        Returns the maximum demand of a parallel section where no
        threads are colocated
        '''
        demand = 0
        obj_to_threads = self.threads_by_object()
        wcet_by_oname  = self.wcet_by_object()
        for oname, threads in obj_to_threads.items():
            fn = wcet_by_oname[oname]
            demand += fn(1) * threads
        return demand

    def min_demand(self):
        '''
        Returns the minimum demand of a parallel section where all
        threads are colocated
        '''
        demand = 0
        obj_to_threads = self.threads_by_object()
        wcet_by_oname  = self.wcet_by_object()
        for oname, threads in obj_to_threads.items():
            fn = wcet_by_oname[oname]
            demand += fn(threads)
        return demand


    @property
    def nodes(self):
        return self._data['nodes']

    @nodes.setter
    def nodes(self, nlist):
        error_msg = 'Parallel section already contains node by name '
        if not isinstance(nlist, list):
            raise Exception('Nodes must be a list')
        for n in nlist:
            found = self.node_by_name(n.name)
            if found:
                raise Exception(error_msg + str(n.name) + ' vs ' + str(found.name))
            self._data['nodes'].append(n)

    @nodes.deleter
    def nodes(self):
        self._data['nodes'] = []

    @property
    def objects(self):
        rval = []
        for node in self.nodes:
            if node.object not in rval:
                rval.append(node.object)
        return rval

    def node_by_name(self, name):
        '''
        Returns a node by name
        '''
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_object(name):
        '''
        Gets an object by name
        '''
        for node in self.nodes:
            if node.object.name == name:
                return node.object
        return None

    def total_threads(self):
        '''
        Returns the sum of all threads of all nodes
        '''
        threads=0
        for node in self.nodes:
            threads += node.threads

        return threads

    def threads_by_object(self):
        '''
        Returns the threads indexed by their object name

         object name | number of threads
        -------------+------------------
                   5 | 1
                   3 | 2
                   9 | 5

        1 thread of object 5, 2 threads of object 3, 5 threads of
        object 9
        '''
        rval = {}
        for node in self.nodes:
            name = node.object.name
            if not name in rval:
                rval[name] = 0
            rval[name] += node.threads
        return rval

    def wcet_by_object(self):
        '''
        Returns the wcet functions of each object by object name

         object name | wcet function
        -------------+------------------
                   5 | wcet_fn_for_5
                   3 | wcet_fn_for_3
                   9 | wcet_fn_for_9
        '''
        rval = {}
        for node in self.nodes:
            name = node.object.name
            rval[name] = node.object.wcet_fn
        return rval

    def cache_availability_by_object(self):
        '''
        Determines the cache availability for each object

        The object availability is defined in terms of the WCET of 1
        thread C(1) and total number of threads of each object T

               C(T)
        1 - ----------
             C(1) * T

        Returns:

           object | cache availability
           -------+-------------------
               1  | cache avalibility of 1 in [0, 1)
               5  | [0, 1)
        '''
        thread_table = self.threads_by_object()
        wcet_table = self.wcet_by_object()
        ca_table = {}
        for obj, threads in thread_table.items():
            wcet_fn = wcet_table[obj]
            obj_total = wcet_fn(1) * threads
            obj_colo  = wcet_fn(threads)
            ca_table[obj] = 1 - (obj_colo / obj_total)
            logging.info(f'{obj} factor:{ca_table[obj]}')

        return ca_table

    def max_wcet_node(self):
        '''
        Returns the node with the maximum WCET contribution to this
        parallel section
        '''
        if len(self.nodes) == 1:
            return self.nodes[0]

        node = max(*self.nodes, key=lambda n:n.bound())
        return node

    def candidate_pairs(self):
        '''
        Returns all pairs of nodes that could be colocated

           +- pair- +
           |        |
        [ [node, node], [node, node], [node, node] ... ]
        '''
        pairs = []
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                left = self.nodes[i]
                right = self.nodes[j]
                if left.object.name != right.object.name:
                    continue
                pairs.append([left, right])
        return pairs

    def colo_cp_ext(self, a, b):
        '''
        Simulates the colocation of nodes a and b, returns the
        extension of the critical path of the critical section

        Raises an exception if the two nodes cannot be colocated
        '''
        anode = self.node_by_name(a.name)
        bnode = self.node_by_name(b.name)
        cnode = self.critical_node()

        if anode == None:
            raise Exception(f'{a.name} is not in the section')
        if bnode == None:
            raise Exception(f'{b.name} is not in the section')

        wcetfn = anode.object.wcet_fn
        total = wcetfn(anode.threads + bnode.threads)

        ext = 0
        if total > cnode.bound():
            ext = total - cnode.bound()

        logging.debug(f'Critical node {cnode.name} bound '
                      f'{cnode.bound()} '
                      f'Colocating <{anode.name},{bnode.name}> has a '
                      f'bound of {total}')

        return ext

    def colo_work_reduction(self, a, b):
        '''
        Simulates the colocation of nodes a nd b, returns the
        reduction of workload.

        Raises an exception on input error
        '''
        left = self.node_by_name(a.name)
        right = self.node_by_name(b.name)

        if left == None:
            raise Exception('a is not in the section')
        if right == None:
            raise Exception('a is not in the section')

        work = left.bound() + right.bound()
        wcetfn = left.object.wcet_fn
        diff = work - wcetfn(left.threads + right.threads)

        return diff


    def colocate(self, a, b):
        '''
        Colocates nodes a and b
        '''
        # Will throw an exception if they cannot be colocated
        ext = self.colo_cp_ext(a, b)
        cnode = self.critical_node()
        expected_length = cnode.bound() + ext

        a.threads += b.threads
        idx = self.nodes.index(b)
        del self.nodes[idx]

        cnode = self.critical_node()
        if expected_length != self.critical_node().bound():
            logging.debug(f'Previous critical path length '
                          f'{expected_length - ext}'
                          f' expected length {expected_length}'
                          f' does not match actual length ',
                          cnode.bound())

    def critical_node(self):
        '''
        Returns the node with the greatest contribution to the
        critical path of the parallel section
        '''
        maxbound = 0
        cnode = None
        for node in self.nodes:
            if maxbound > node.bound():
                continue
            maxbound = node.bound()
            cnode = node
        return cnode


class WCETEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, WCET):
            return {
                'base' : obj._base,
                'incr' : obj._incr
            }
        return super().default(obj)

class ForkJoinObjectEncoder(WCETEncoder):
    def default(self, obj):
        if isinstance(obj, ForkJoinObject):
            return {
                'name' : obj.name,
                'wcet' : obj.wcet_fn
            }
        return super().default(obj)

class ForkJoinNodeEncoder(ForkJoinObjectEncoder):
    def default(self, obj):
        if isinstance(obj, ForkJoinNode):
            return {
                'name'    : obj.name,
                'threads' : obj.threads,
                'object'  : obj.object.name
            }
        return super().default(obj)

class ParallelSectionEncoder(ForkJoinNodeEncoder):
    def default(self, obj):
        if isinstance(obj, ParallelSection):
            return obj.nodes
        return super().default(obj)


class ForkJoinTaskEncoder(ParallelSectionEncoder):
    def default(self, obj):
        if isinstance(obj, ForkJoinTask):
            return {
                'name': obj._data['name'],
                'deadline' : obj._data['deadline'],
                'sections' : obj._data['sections'],
                'serial-nodes' : obj._data['ser_nodes'],
                'objects' : obj._data['objects'],
                'results' : obj._data['results']
            }
        return super().default(obj)

class ForkJoinTaskSetEncoder(ForkJoinTaskEncoder):
    def default(self, obj):
        if isinstance(obj, ForkJoinTaskSet):
            return {
                'name'  : obj.name,
                'tasks' : obj.tasks
            }
        return super().default(obj)

class ForkJoinObjectDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook,
                                  *args, **kwargs)
    def object_hook(self, dct):
        if 'name' in dct:
            o = ForkJoinObject(dct['name'])
            o.wcet_fn = dct['wcet']
            return o
        if 'base' in dct:
            c = WCET(b=dct['base'], i=dct['incr'])
            return c

class ForkJoinTaskDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook,
                                  *args, **kwargs)
        # Nodes in this list need their object assigned when it is
        # parsed
        self._pobj = {}
        self._objs = {}
    def object_hook(self, dct):
        if 'base' in dct:
            # WCET
            c = WCET(dct['base'], dct['incr'])
            return c
        if 'wcet' in dct:
            # ForkJoinObject
            o = ForkJoinObject(dct['name'])
            o.wcet_fn = dct['wcet']
            self.cache_add(o)
            return o
        if 'threads' in dct:
            # ForkJoinNode
            n = ForkJoinNode(dct['name'])
            n.threads = dct['threads']
            oname = dct['object']
            o = self.cache_find(oname)
            if o:
                n.object = o
            else:
                self.pending_add(n, oname)
            return n
        if 'deadline' in dct:
            # ForkJoinTask
            t = ForkJoinTask(dct['name'])
            t.deadline = dct['deadline']
            t.objects = dct['objects']
            t.serial_nodes = dct['serial-nodes']
            for secnodes in dct['sections']:
                p = ParallelSection()
                p.nodes = secnodes
                t.add_section(p)
            if 'results' in dct:
                for k, v in dct['results'].items():
                    t.set_result(k, v)
            return t
        # Catch all
        return dct


    def cache_add(self, o):
        '''Adds a fork join object to the cache'''
        if o.name in self._objs:
            return
        self._objs[o.name] = o
        if o.name not in self._pobj:
            # No pending nodes
            return
        for obj in self._pobj[o.name]:
            obj.object = o
        del self._pobj[o.name]


    def cache_find(self, oname):
        '''Finds a fork join object in the cache'''
        if oname in self._objs:
            return self._objs[oname]
        return None

    # Adds a node to the pending-object list
    def pending_add(self, node, oname):
        '''Adds a node to the pending-object list waiting for object
           with name oname'''
        if oname in self._pobj:
            self._pobj[oname].append(node)
        else:
            self._pobj[oname] = [node]


class ForkJoinTaskSetDecoder(ForkJoinTaskDecoder):
    def object_hook(self, dct):
        if 'tasks' in dct:
            taskset = ForkJoinTaskSet(dct['name'])
            taskset.tasks = dct['tasks']
            return taskset
        return super().object_hook(self, dct)
