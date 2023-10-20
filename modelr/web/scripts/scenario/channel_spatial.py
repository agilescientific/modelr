'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import matplotlib

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers
from modelr.web.urlargparse import rock_properties_type

from modelr.web.util import modelr_plot

import modelr.modelbuilder as mb
from bruges.reflection import zoeppritz
from bruges.filters import ricker
from svgwrite import rgb

# This is required for Script help
short_description = 'Spatial view of a channel'

def add_arguments(parser):
    default_parser_list = [
                           'base1','base2','overlay1','overlay2',
                           'opacity','f', 'theta','colourmap'
                           ]
    
    default_parsers(parser,default_parser_list)
    
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Upper rock type',
                        required=True,
                        default='2000,1000,2200'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                        help='Rock type of the channel',
                        required=True,
                        default='2200,1100,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                        help='Lower rock type',
                        required=False,
                        default='2500,1200,2600'
                        )
    
    parser.add_argument('tslice',
                        type=float, 
                        help='time [ms] along which to plot instantaneous amplitude ',
                        required=True,
                        default=150
                        )
                        


                        
    return parser

def run_script(args):
    matplotlib.interactive(False)
    
    """if args.transparent == 'False' or args.transparent == 'No':
        transparent = False
    else:
        transparent = True"""
    from functools import partial
    args.ntraces = 300
    args.pad = 150
    args.reflectivity_method = zoeppritz
    args.title = 'Channel Model - Spatial Cross Section'
    args.wavelet = partial(ricker, return_t=False)
    args.wiggle_skips = 10
    args.aspect_ratio = 1
    args.thickness = 50
    args.margin=1
    args.slice='spatial'
    args.trace = 0
    
    transparent = False
    # This is a hack to conserve colors
    l1 = (150,110,110)
    l2 = (110,150,110)
    l3 = (110,110,150)
    layers= [l1,l2]
    colourmap = { rgb(150,110,110): args.Rock0,
                  rgb(110,150,110): args.Rock1 }
    
    if not isinstance(args.Rock2, str):
        colourmap[rgb( 110,110,150)] = args.Rock2
        layers.append( l3 )
    # Get the physical model (an array of rocks)    
    model = mb.channel(pad = args.pad,
                       thickness = args.thickness,
                       traces = args.ntraces,
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
