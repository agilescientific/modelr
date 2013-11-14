'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
from argparse import ArgumentParser
from modelr.reflectivity import get_reflectivity, do_convolve
from modelr.modelbuilder import wedge
import matplotlib
import matplotlib.pyplot as plt
from modelr.web.urlargparse import rock_properties_type, reflectivity_type, wavelet_type
from modelr.rock_properties import MODELS
from modelr.web.util import return_current_figure
import numpy as np
from modelr.web.util import wiggle

short_description = 'Create a simple wedge model.'

def add_arguments(parser):
    
    parser.add_argument('title', 
                        default='Plot',
                        type=str,
                        help='The title of the plot'
                        )
                        
    parser.add_argument('pad',
                        default=50,
                        type=int,
                        help='The time in milliseconds above and below the wedge'
                        )
                        
    parser.add_argument('thickness',
                        default=50,
                        type=int,
                        help='The maximum thickness of the wedge'
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
                        help='ricker, ormsby, sweep',
                        default='ricker'
                        )

    return parser


def run_script(args):
    
    matplotlib.interactive(False)

    # Get the physical model (an array of rocks)    
    model = wedge(traces = args.ntraces,
                   pad = args.pad,
                   thickness = args.thickness,
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
