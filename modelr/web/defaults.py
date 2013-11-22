'''
Created on November 2013

@author: Matt Hall
'''

from modelr.web.urlargparse import reflectivity_type, wavelet_type
from modelr.web.urlargparse import WAVELETS
from modelr.reflectivity import MODELS

def default_parsers(parser, list_of_parsers):
    
    if 'title' in list_of_parsers:        
        parser.add_argument('title', 
                            default='Plot',
                            type=str,
                            help='The title of the plot'
                            )
    
    if 'ntraces' in list_of_parsers:        
        parser.add_argument('ntraces',
                            default=300,
                            type=int,
                            help='Number of traces'
                            )
        
    if 'pad' in list_of_parsers:
        parser.add_argument('pad',
                            default=50,
                            type=int,
                            help='The time in milliseconds above and below the wedge'
                            )
                            
    if 'reflectivity_method' in list_of_parsers:
        parser.add_argument('reflectivity_method',
                            type=reflectivity_type,
                            help='Algorithm for calculating reflectivity',
                            default='zoeppritz',
                            choices=MODELS.keys()
                            ) 
                                
    if 'theta' in list_of_parsers:
        parser.add_argument('theta',
                            type=int,
                            action='list',
                            help='Angle of incidence',
                            default=0
                            )
                            
    if 'f' in list_of_parsers:
        parser.add_argument('f',
                            type=int,
                            action='list',
                            help='Frequency of wavelet',
                            default=25
                            )
                            
    if 'colour' in list_of_parsers:
        parser.add_argument('colour',
                            type=str,
                            help='Matplotlib colourmap, ageo.co/modelrcolour',
                            default='Greys'
                            )
        
    if 'display' in list_of_parsers:
        parser.add_argument('display',
                            type=str,
                            help='Type of seismic display',
                            choices=['wiggle', 'variable-density', 'both'],
                            default='variable-density'
                            )
        
    if 'wavelet' in list_of_parsers:
        parser.add_argument('wavelet',
                            type=wavelet_type,
                            help='Wavelet type',
                            default='ricker',
                            choices=WAVELETS.keys()
                            )
                                        
    return parser