import json
import argparse

class RunContext:
    def __init__(self, namespace=None, jsonfile=None):
        '''
        Constructor

        namespace: must be an argparse.Namespace
        jsonfile: path to json file
        '''
        if jsonfile:
            self.loadJSON(jsonfile)
        if namespace:
            self.ns = namespace

    @property
    def ns(self):
        return self._ns

    @ns.setter
    def ns(self, value):
        if not isinstance(value, argparse.Namespace):
            raise Exception('value must be an argparse.Namespace')

        self._data = {
            'par-secs'  : [value.sections_lb,     value.sections_ub],
            'objs'      : [value.objects_lb,      value.objects_ub],
            'bases'     : [value.base_lb,         value.base_ub],
            'incrs'     : [value.incremental_lb,  value.incremental_ub],
            'deadlines' : [value.deadline_lb,     value.deadline_ub],
            'threads'   : [value.threads_lb,      value.threads_ub],
            'set-sizes' : [value.set_size_lb,     value.set_size_ub],
            'tasks'     : value.tasks,
            'task-sets' : value.task_sets,
        }
        self._ns = value

    @ns.deleter
    def ns(self):
        del self._data
        del self._ns
    
    def toJSON(self):
        '''
        JSON Encoder Method
        '''
        return json.dumps(self._data, indent=4)


    def loadJSON(self, path):
        '''
        Loads a JSON file into the run context,        '''
        with open(path, 'r') as fp:
            self._data = json.load(fp)

    def dumpJSON(self, path):
        '''
        Writes a JSON file representing the current run context
        '''
        with open(path, 'w') as fp:
            json.dump(self._data, fp, indent=4)
    
    @property
    def objs(self):
        return self._data['objs']

    @property
    def sections(self):
        return self._data['par-secs']

    @property
    def bases(self):
        return self._data['bases']
    
    @property
    def incrs(self):
        return self._data['incrs']

    @property
    def tasks(self):
        return self._data['tasks']

    @property
    def tasksets(self):
        return self._data['task-sets']
    
    @property
    def threads(self):
        return self._data['threads']

    @property
    def deadlines(self):
        return self._data['deadlines']

    @property
    def set_sizes(self):
        return self._data['set-sizes']
