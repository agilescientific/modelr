'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.web.urlargparse import rock_properties_type

from modelr.web.util import multi_plot

import modelr.modelbuilder as mb
from modelr.web.defaults import default_parsers
from svgwrite import rgb

short_description = ('Look at plots '
                     'across spatial, offset, and frequency '
                     'cross-sections')


def add_arguments(parser):

    default_parser_list = [
                           'title',
                           'colourmap',
                           'wiggle_skips',
                           'aspect_ratio',
                           'base1','base2','overlay1','overlay2',
                           'opacity'
                           ]
    
    default_parsers(parser,default_parser_list)

    parser.add_argument('f',
                        type=float,
                        default=10.0,
                        help="Wavelet CF to use for cross section")

    parser.add_argument('theta',
                        type=float,
                        default=20.0,
                        help="Offset angle to use for cross section")
    
    parser.add_argument('slice',
                        type=str,
                        help='Slice to return',
                        default='spatial',
                        choices=['spatial', 'angle', 'frequency']
                        )
                        
    parser.add_argument('trace',
                        type=int,
                        help='Trace to use for non-spatial cross section',
                        default=150
                        )
    
    parser.add_argument('tslice',
                        type=float, 
                        help='time [s] along which to plot instantaneous amplitude ',
                        required=True,
                        default=0.050
                        )

    return parser

def run_script(earth_model, seismic_model, plot_args):

    # Get the axis
    traces = range(seismic_model.seismic.shape[1])
    f = seismic_model.wavelet_cf()
    theta = seismic_model.offset_angles()
    plot_args.xscale = seismic_model.f_res

 
    return multi_plot(earth_model.get_data(),
                       seismic_model.reflectivity,
                       seismic_model.seismic, traces, f, theta,
                       plot_args)
        
    

    
if __name__ == '__main__':
    main()
