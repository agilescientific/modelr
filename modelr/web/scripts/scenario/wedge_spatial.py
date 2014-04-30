'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers
from modelr.web.urlargparse import rock_properties_type
from agilegeo.avo import zoeppritz

from modelr.web.util import modelr_plot
from agilegeo.wavelet import ricker

import modelr.modelbuilder as mb

from svgwrite import rgb

short_description = 'Spatial view of a simple wedge model'

def add_arguments(parser):
    
    default_parser_list = [
                           'base1','base2','overlay1','overlay2',
                           'opacity', 'colourmap','f','theta'
                           ]
    
    default_parsers(parser,default_parser_list)
    
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Rock properties of upper rock '+
                        '[Vp,Vs, rho]',
                        required=True,
                        default='2000,1000,2200'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                        help='Rock properties of middle rock ' +
                        '[Vp, Vs, rho]',
                        required=True,
                        default='2200,1100,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                        help='Rock properties of lower rock ' +
                        '[Vp, Vs, rho]',
                        required=False,
                        default='2500,1200,2600'
                        )

    parser.add_argument('tslice',
                        type=float, 
                        help='time [s] along which to plot instantaneous amplitude ',
                        required=True,
                        default=0.150
                        )
                      
    parser.add_argument('scale',
                        type=float,
                        action='list', 
                        help='0 for auto scale, and (optional) clip percentile (e.g. 99)',
                        required=True,
                        default='1.0,99'
                        )

    return parser


def run_script(args):
    
    matplotlib.interactive(False)

    args.ntraces = 300
    args.pad = 150
    args.reflectivity_method = zoeppritz
    args.title = 'Wedge model - spatial cross section'
    args.wavelet = ricker
    args.wiggle_skips = 10
    args.aspect_ratio = 1
    args.margin=1
    args.left = (0,0)
    args.right = (0,50)
    args.slice='spatial'
    args.trace = 0
    
    left = (args.left[0], args.left[1])
    right = (args.right[0], args.right[1])


    l1 = (150,110,110)
    l2 = (110,150,110)
    l3 = (110,110,150)
    layers= [l1,l2]

    # This is a hack to conserve colors
    colourmap = { rgb(l1[0],l1[1],l1[2]): args.Rock0,
                  rgb(l2[0],l2[1],l2[2]): args.Rock1 }
    
    if not isinstance(args.Rock2, str):
        colourmap[rgb( l3[0],l3[1],l3[2])] = args.Rock2
        layers.append( l3 )
    
    model = mb.body( traces = args.ntraces,
                     pad = args.pad,
                     margin=args.margin,
                     left = left,
                     right = right,
                     layers = layers
                   )

    return modelr_plot( model, colourmap, args )

    
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

