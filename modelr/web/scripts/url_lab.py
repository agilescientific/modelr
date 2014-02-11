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

from modelr.web.util import modelr_plot


from modelr.reflectivity import get_reflectivity, do_convolve
import modelr.modelbuilder as mb
from svgwrite import rgb

short_description = 'Use a model from a file on the web.'

def add_arguments(parser):
    
    default_parser_list = ['ntraces',
                           'reflectivity_method',
                           'title',
                           'theta',
                           'f',
                           'colourmap',
                           'wavelet',
                           'wiggle_skips',
                           'base1','base2','overlay1','overlay2',
                           'opacity', 'aspect_ratio'
                           
                           ]
    
    default_parsers(parser,default_parser_list)
    
                        
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Rock properties of rock 0 [Vp,Vs, rho]',
                        required=True,
                        default='2350,1150,2400'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                        help='Rock properties of rock 1 [Vp, Vs, rho]',
                        required=True,
                        default='2150,1050,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                        help='Rock properties of rock 2 [Vp, Vs, rho]',
                        required=False,
                        default='2500,1250,2600'
                        )
    
    parser.add_argument('Rock3',
                        type=rock_properties_type, 
                        help='Rock properties of rock 3 [Vp, Vs, rho]',
                        required=False,
                        default='2600,1350,2700'
                        )
    
    parser.add_argument('url',
                        type=str, 
                        help='a URL for an image with 3 colours',
                        required=True,
                        default='http://www.subsurfwiki.org/mediawiki/images/4/41/Modelr_test_ellipse.png'
                        )
    
    parser.add_argument('rocks',
                        type=int, 
                        help='the number of rocks in the model',
                        required=False
                        )
    
    parser.add_argument('minimum',
                        type=int, 
                        help='the minimum impedance (or use Rocks)',
                        required=False
                        )
    
    parser.add_argument('maximum',
                        type=int, 
                        help='the maximum impedance (or use Rocks)',
                        required=False
                        )

    parser.add_argument('slice',
                        type=str,
                        help='Slice to return',
                        default='spatial',
                        choices=['spatial', 'angle', 'frequency']
                        )
                        
    parser.add_argument('trace',
                        type=int,
                        help='Trace to use for non-spatial slice',
                        default=0
                        )
    
    return parser


def run_script(args):
    from modelr.constants import dt, duration
    matplotlib.interactive(False)
 
    Rprop0 = args.Rock0 
    Rprop1 = args.Rock1
    Rprop2 = args.Rock2
    Rprop3 = args.Rock3
    
    colourmap = {}

    if isinstance(Rprop0, str):
        Rprop0 = None
    else:
        colourmap[rgb(255,255,255)] = Rprop0 
        
    if isinstance(Rprop1, str):
        Rprop1 = None
    else:
        colourmap[rgb( 255,0,0 )] = Rprop1 
        
    if isinstance(Rprop2, str):
        Rprop2 = None
    else:
        colourmap[rgb( 0,0,255 )] = Rprop2 
        
    if isinstance(Rprop3, str):
        Rprop3 = None
    else:
        colourmap[3] = Rprop3 
    
    if not isinstance(args.rocks, int):
        colours = 0
    else:
        colours = args.rocks

    
    colours = ((255,255,255),(255,0,0), (0,0,255) )
    model = mb.web2array(args.url,
                         colours = colours
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
