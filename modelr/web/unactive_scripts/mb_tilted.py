'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.reflectivity import get_reflectivity, do_convolve

import modelr.modelbuilder as mb

from modelr.web.urlargparse import rock_properties_type, \
     reflectivity_type, wavelet_type
from modelr.web.urlargparse import WAVELETS

from modelr.rock_properties import MODELS

from modelr.web.util import return_current_figure
from modelr.web.util import wiggle


short_description = 'Create a simple tilted model.'

def add_arguments(parser):
    
    parser.add_argument('title', 
                        default='Plot',
                        type=str,
                        help='The title of the plot'
                        )
                        
    parser.add_argument('pad',
                        default=50,
                        type=int,
                help='Ttime in milliseconds above and below the wedge'
                        )
                        
    parser.add_argument('thickness',
                        default=50,
                        type=int,
                        help='The vertical thickness of the slab'
                        )
                        
    parser.add_argument('ntraces',
                        default=300,
                        type=int,
                        help='Number of traces'
                        )
    
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                help='Rock properties of upper rock [Vp,Vs, rho]',
                        required=True,
                        default='2350,1150,2400'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                help='Rock properties of middle rock [Vp, Vs, rho]',
                        required=True,
                        default='2150,1050,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                help='Rock properties of lower rock [Vp, Vs, rho]',
                        required=False,
                        default='2500,1250,2600'
                        )
    
    parser.add_argument('reflectivity_method',
                        type=reflectivity_type,
                        help='Algorithm for calculating reflectivity',
                        default='zoeppritz',
                        choices=MODELS.keys()
                        ) 
                         
    parser.add_argument('theta',
                        type=float,
                        help='Angle of incidence',
                        default='0'
                        )
                        
    parser.add_argument('f',
                        type=float,
                        action='list',
                        help='Frequency of wavelet',
                        default=25
                        )
                        
    parser.add_argument('colour',
                        type=str,
                        help='Matplotlib colourmap',
                        default='Greys'
                        )
    
    parser.add_argument('display',
                        type=str,
                        help='wiggle, image, or both',
                        default='image'
                        )

    parser.add_argument('wavelet',
                        type=wavelet_type,
                        help='Wavelet type',
                        default='ricker',
                        choices=WAVELETS.keys()
                        )

    return parser


def run_script(args):
    
    matplotlib.interactive(False)
 
    Rprop0 = args.Rock0 
    Rprop1 = args.Rock1
    Rprop2 = args.Rock2
    
    if isinstance(Rprop2, str):
        Rprop2 = None
    
    model = mb.tilted(traces = args.ntraces,
                   pad = args.pad,
                   thickness = args.thickness,
                   layers = (Rprop0,Rprop1,Rprop2)
                   )

    colourmap = { 0: Rprop0, 1: Rprop1, 2: Rprop2 }
        
    reflectivity = get_reflectivity(data=model,
                                    colourmap = colourmap,
                                    theta = args.theta,
                                    f = args.f,
                                    reflectivity_method =
                                      args.reflectivity_method
                                    )
    
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
