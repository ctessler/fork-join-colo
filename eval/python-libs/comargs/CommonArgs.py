import argparse
import logging

class CommonArgs:
    '''
    A container for common command line arguments for each of the
    simulation scripts. The container uses the phrase 'context' to
    refer to values of an instance, ie. the values of the command line
    parameters for a given invocation.
    '''
    
    def __init__(self, argparser=None):
        '''
        Constructor
        parser  : an existing argparse.Namespace instance which these
                  options will be appended to
        '''
        if argparser:
            self.parser = argparser
        else:
            c = argparse.ArgumentDefaultsHelpFormatter
            self.parser = argparse.ArgumentParser(formatter_class=c)
        self.add_arguments()

    def add_arguments(self):
        p = self.parser
        g = p.add_argument_group('Common Arguments')
        g.add_argument('-v', '--verbose', action='count', default=0,
                       help='Increases the logging level')
        g.add_argument('-l', '--log-file', action='store',
                       help='Execution run log file')
        g.add_argument('-c', '--cfg', type=str,
                       help='JSON file of the run context. When '
                       'provided as input, it is parsed before the '
                       'command line arguments')
        g.add_argument('-u', '--dump-cfg', type=str,
                       help='Dumps the JSON configuration file for '
                       'to repeat this invocation')
        g.add_argument('dir', action='store', nargs='?',
                       help='A context directory, containing the task'
                       'sets and results')
        g.add_argument('-T', '--timeout', type=int,
                       help='Timeout in seconds (0 is forever)',
                       default=0)
        g.add_argument('-X', '--skip-exact', action='store_true',
                       help='Skips the exact methods', default=False)
        g.add_argument('-W', '--skip-dag', action='store_true',
                       help='Skips the DAG methods', default=False)

    @property
    def parser(self):
        '''Gets the current argument parser'''
        return self._parser

    @parser.setter
    def parser(self, value):
        if not isinstance(value, argparse.ArgumentParser):
            raise Exception('parser must an argparse.Namespace')
        self._parser = value

    @parser.deleter
    def parser(self):
        del self._parser

    @property
    def namespace(self):
        '''
        Gets the parsed command line arguments
        '''
        if not hasattr(self, '_ns'):
            self._ns = self.parser.parse_args()
            self._init_logging(self._ns.verbose)
        return self._ns
        
    @namespace.setter
    def namespace(self, value):
        raise Exception('Cannot set the namespace')

    @namespace.deleter
    def namespace(self):
        del self._ns

    def _init_logging(self, verbosity):
        # verbosity must be a valid integer
        level = verbosity * -10 + logging.INFO
        logargs = {
#            'format'  : "%(asctime)s.%(msecs)03d [%(levelname)s] "
#                        "%(filename)s:%(lineno)03d > %(message)s",
            'format'  : "%(asctime)s [%(levelname)s] > %(message)s",
            'datefmt' : "%H:%M:%S",
            'level'   : level
        }
        if self._ns.log_file:
            logargs['filename'] = self._ns.log_file
            
        logging.basicConfig(**logargs)
        logging.debug(f'Debug logging enable')
        
