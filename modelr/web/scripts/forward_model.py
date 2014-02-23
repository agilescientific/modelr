'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.web.urlargparse import rock_properties_type

from modelr.web.util import modelr_plot

import modelr.modelbuilder as mb
from modelr.web.defaults import default_parsers
from svgwrite import rgb

short_description = ('Run a forward seismic convolution model '
                     'across spatial, offset, and frequency '
                     'cross-sections')

def add_cs_arguments(parser):

    parser.add_argument('slice',
                        default='spatial',
                        choices=['spatial', 'angle',
                                 'frequency'],
                        help='Model Cross-Section')
    return parser

def add_seismic_arguments(parser, cross_section):

    if cross_section == 'spatial':
        
        default_list = ['reflectivity_method']
        default_parsers(parser, default_list)
        parser.add_argument('f', type=float, default=20.0,
                                     help="Wavelet Frequency")
        parser.add_argument('theta', type=float, default=0.0,
                            help="Offset Angle")
        return parser
    
    elif cross_section == 'angle':
        
        default_list = ['reflectivity_method']
        default_parsers(parser, default_list)
        parser.add_argument('f', type=float, default=20.0,
                            help="Wavelet Frequency")
        parser.add_argument('trace', type=int, default=0,
                            help="Trace Location")
        parser.add_argument('theta', type=float, default='0,45,.5',
                            action='list',
                            help='Offset Angle (min, max, res)')
        return parser
    
    elif cross_section == 'wavelet':
        default_list = ['reflectivity_method']
        default_parsers(parser, default_list)
        parser.add_argument('trace', type=int, default=0,
                            help="Trace Location")
        parser.add_argument('theta', type=float, default='0,45,.5',
                            action='list',
                            help='Offset Angle(min, max, resolution)')
        parser.add_argument('f', default='5, 120, 1', type=float,
                            action='list',
                            help='Wavelet Frequencies (min,max, res)')

    else:
        raise TypeError

def add_plot_arguments(parser):

    default_list = ['title', 'base1', 'base1', 'overlay1',
                    'overlay2']
    default_parsers(parser)

    return parser

def run_script(model, rock_map, args):

    return modelr_plot(model, rock_map, args)

    
def main():
    parser = ArgumentParser(usage=short_description,
                            description=__doc__
                            )
                            
    parser.add_argument('time',
                        default=150,
                        type=int, 
                        help='The size in milliseconds of the plot'
                        )
                        
    args = parser.parse_args()
    run_script(args)
    
if __name__ == '__main__':
    main()
