'''
====================
modelr.web.urlparse
====================

.. seealso:: http://docs.python.org/dev/library/argparse.html
'''
import sys
from urlparse import urlparse, parse_qs
from argparse import Namespace
import json
from modelr.constants import WAVELETS
from modelr.constants import REFLECTION_MODELS
import numpy as np

def rock_properties_type(str_input):
    from modelr.rock_properties import RockProperties
    args = str_input.split(',')
    assert ((len(args) == 3) or (len(args)==6))

    if (len(args) == 3):
        return RockProperties(vp = float(args[0]),
                              vs = float(args[1]), 
                              rho = float(args[2]))
    
    return RockProperties(vp = float(args[0]),
                          vs = float(args[1]), 
                          rho = float(args[2]),
                          vp_sig = float(args[3]), 
                          vs_sig = float(args[4]),
                          rho_sig = float(args[5]))


def earth_model_type(str_input):

    data = json.loads(str_input)

    return {"image": data["image"],
            "mapping": data["mapping"]}

    

def wavelet_type(str_input):
    '''
    To be used as the 'type' value in an Argument. 
    
    Takes a string as input and returns an arbitrary value.
    
    Example::
                     
        parser.add_argument('wavelet', type=wavelet_type, help='... ',
                            default='ricker', choices=WAVELETS.keys())
     
    '''
    
    return WAVELETS[str_input]

def reflectivity_type(str_input):
    '''
    To be used as the 'type' value in an Argument. 
    
    Takes a string as input and returns an arbitrary value.
    
    Example::
        
        parser.add_argument('reflectivity_model',
        type=reflectivity_type, help='... ', default='zoeppritz',
        choices=MODELS.keys())
     
    ''' 
    return REFLECTION_MODELS[str_input]


    
 
class Argument(object):
    '''
    A place holder for a url argument.
    '''
    def __init__(self, name, required=False, default=None, type=str,
                 action='store', help='', choices=None,
                 interface=None, range=None):
        self.name = name
        self.required = required
        self.default = default
        self.type = type
        self.action = action
        self.help = help
        self.choices = choices
        self.interface = interface
        self.range = range

        
    
    def parse_arg(self, args):
        if not args or not args[0] or args[0] == 'null':
            if self.required:
                raise ArgumentError("missing argument %r" %
                                    (self.name,))
            else:
                return self.default
        
        arg = args[0]
        if self.action != 'list':
            if self.choices is not None and arg not in self.choices:
                raise ArgumentError("argument %s is invalid:" +
                                    " must be one of %r (got %r)" %
                                    (self.name, self.choices, arg))
            try:
                arg = self.type(arg)
                
            except:
                raise ArgumentError("argument %s: invalid %s" +
                                    " value: %r" %
                                    (self.name, self.type.__name__,
                                     arg))
            
            return arg
        else:
            new_args = []
            for arg in arg.split(','):
                try:
                    value = self.type(arg)
                 
                except:
                    raise ArgumentError("argument %s: invalid %s"+
                                        " value: %r" %
                                        (self.name,
                                         self.type.__name__, arg))
                
                new_args.append(value)
            
            return new_args
            
    
    @property
    def json_dict(self):
        return {
        'name':self.name,
        'required': self.required,
        'default': self.default,
        'type':self.type.__name__,
        'action':self.action,
        'help': self.help,
        'choices': self.choices,
        'interface': self.interface,
        'range': self.range
        }

    @property
    def html_help(self):
        return '<li><b>%s</b>: %s</li>\n' % (self.name, self.help)
        
        
    
class ArgumentError(Exception):
    '''
    Exception to be called when arguments are not as expected by the
    parser.
    '''

class SendHelp(Exception):
    '''
    Exception to be called when the help argument is found.
    '''
    def __init__(self, html):
        Exception.__init__(self, html)
        self.html = html

class URLArgumentParser(object):
    '''
    Parse a key=value arguments in a url string.
    
    Modeled after http://docs.python.org/dev/library/argparse.html
    '''
    
    def __init__(self, description='No Description'):
        '''
        Constructor
        '''
        self.description = description
#        self.arguments = {'help': Argument('help')}
        self.arguments = []
        
    def add_argument(self, name, required=False, default=None,
                     type=str, action='store', help='', choices=None,
                     interface=None, range=None):
        '''
        add an argument
        '''
        arg = Argument(name, required, default, type, action,
                       help, choices, interface, range)
        self.arguments.append(arg)
        
    def parse_params(self, params):
        '''
        parse the arguments gotten by urlparse.parse_qs
        '''
        result = dict()
        
        if 'help' in params:
            params.pop('help')
            self.raise_help()

        for parser in self.arguments:

           
            arg = params.pop(parser.name, None)
            if np.ndim(arg) == 0:
                arg = [arg]
                
            value = parser.parse_arg(arg)
            result[parser.name] = value
            
        if params:
            key, value = params.popitem()
            raise ArgumentError("got unexpected argument %r" % (key,))
            
        return Namespace(**result)
    
    def parse_ulr(self, path):
        '''
        parse a url into its argument. 
        '''

        uri = urlparse(path)
        params = parse_qs(uri.query)
        
        return self.parse_params(params)
        
        
    @property
    def json_data(self):
        obj = {'description': self.description,
               'arguments': [arg.json_dict
                             for arg in self.arguments]}
        return json.dumps(obj)
    
    @property
    def help_html(self):
        
        arguments = '\n'.join(arg.html_help for arg in
                              self.arguments)
        return '<p>%s</p><ul>\n%s</ul>' % (self.description,
                                           arguments)
        
    def raise_help(self):
        raise SendHelp(self.help_html)
    
    
def main():
    path = sys.argv[1]
    
    parser = URLArgumentParser('description')
    
    parser.add_argument('script', required=True, type=str)
    
    
if __name__ == '__main__':
    main()
