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

short_description = ('Look at plots '
                     'across spatial, offset, and frequency '
                     'cross-sections')


def add_arguments(parser):

    default_parser_list = [
                           'title',
                           'theta',
                           'f',
                           'colourmap',
                           'wiggle_skips',
                           'aspect_ratio',
                           'base1','base2','overlay1','overlay2',
                           'opacity'
                           ]
    
    default_parsers(parser,default_parser_list)

    parser.add_argument('slice',
                        type=str,
                        help='Slice to return',
                        default='spatial',
                        choices=['spatial', 'angle', 'frequency']
                        )
                        
    parser.add_argument('trace',
                        type=int,
                        help='Trace to use for non-spatial slice',
                        default=150
                        )
    
    parser.add_argument('tslice',
                        type=float, 
                        help='time [s] along which to plot instantaneous amplitude ',
                        required=True,
                        default=0.050
                        )


    return parser

def run_script(args):
    pass

    
if __name__ == '__main__':
    main()
