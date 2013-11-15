'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''

import matplotlib
import matplotlib.pyplot as plt

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers

from modelr.reflectivity import get_reflectivity, do_convolve

import modelr.modelbuilder as mb

from modelr.web.urlargparse import rock_properties_type
from modelr.web.util import return_current_figure
from modelr.web.util import wiggle


short_description = 'Create a simple wedge model.'

def add_arguments(parser):
    
    default_parser_list = ['ntraces',
                           'pad',
                           'colour',
                           'reflectivity_method',
                           'title',
                           'theta',
                           'f',
                           'display',
                           'colour',
                           'wavelet'
                           ]
    
    default_parsers(parser,default_parser_list)
    
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Rock properties of upper rock [Vp,Vs, rho]',
                        required=True,
                        default='2000,1000,2200'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                        help='Rock properties of middle rock [Vp, Vs, rho]',
                        required=True,
                        default='2200,1100,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                        help='Rock properties of lower rock [Vp, Vs, rho]',
                        required=False,
                        default='2500,1200,2600'
                        )
    
    parser.add_argument('left',
                        type=int,
                        action='list',
                        default='0,0',                        
                        help='The thickness on the left-hand side'
                        )
                        
    parser.add_argument('right',
                        type=int,
                        action='list',
                        default='0,50',                        
                        help='The thickness on the right-hand side'
                        )
                        
    parser.add_argument('margin',
                        type=int,
                        help='Traces with zero thickness',
                        default=1
                        )

    parser.add_argument('selection',
                        type=str,
                        help='Slice to return',
                        default='thickness',
                        choices=['thickness', 'offset', 'frequency']
                        )

    return parser


def run_script(args):
    
    matplotlib.interactive(False)
    
    left = (args.left[0], args.left[1])
    right = (args.right[0], args.right[1])
    
    model = mb.body(traces = args.ntraces,
                   pad = args.pad,
                   margin=args.margin,
                   left = left,
                   right = right,
                   layers = (args.Rock0,args.Rock1,args.Rock2)
                   )
        

    colourmap = { 0: args.Rock0, 1: args.Rock1 }
    if not isinstance(args.Rock2, str):
        colourmap[2] = args.Rock2
    
    reflectivity = get_reflectivity(data=model,
                                    colourmap = colourmap,
                                    theta = args.theta,
                                    f = args.f,
                                    reflectivity_method = args.reflectivity_method
                                    )
    
    if args.selection == 'frequency':
        warray_amp = do_convolve(args.wavelet, args.f, reflectivity)                        
    elif args.selection == 'offset':
        warray_amp = do_convolve(args.wavelet, args.f, reflectivity)
    else:
        warray_amp = do_convolve(args.wavelet, args.f, reflectivity)
        
                        
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]
    
    if args.display == 'wiggle':        
        wiggle(warray_amp,1)       
    else:
        ax1.imshow( warray_amp, aspect=aspect, cmap=args.colour)
        
    if args.display == 'both':
        wiggle(warray_amp,1)
        plt.gca().invert_yaxis()
        
    plt.title(args.title % locals())
    plt.ylabel('time (ms)')
    plt.xlabel('trace')
    
    return return_current_figure()
    
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
