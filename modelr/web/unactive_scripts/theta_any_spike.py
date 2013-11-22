'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall

The main purpose of this script is to support the Android
app AVO*, which wants a simple gather for a step function.
The app will gather the parameters and pass them via a
URL, and will get a JPG back in return. 
'''
from argparse import ArgumentParser
from modelr.reflectivity import create_theta_spike
import matplotlib
import matplotlib.pyplot as plt
import tempfile
from os import unlink
from modelr.web.urlargparse import reflectivity_type, wavelet_type, \
     WAVELETS
from modelr.web.util import return_current_figure
from modelr.rock_properties import MODELS
import numpy as np

short_description = 'Create a simple gather for a single reflectivity spike'

def add_arguments(parser):
    
    parser.add_argument('title', default='Plot',
                        type=str, help='The title of the plot')
    parser.add_argument('pad', default=50, type=int,
            help='The time in milliseconds above and below the wedge')
    
    parser.add_argument('rc', type=float,
                        help='reflection coeffiecient series',
                        required=True)
    
    parser.add_argument('theta', type=float, action='list',
                        help='Angle of incidence', default='0,60,1')
    
    parser.add_argument('wavelet', type=wavelet_type, help='wavelet',
                        default="ricker", choices=WAVELETS.keys())
    
    parser.add_argument('f', type=float, action='list',
                        help='frequencies', default=25)
    
    parser.add_argument('reflectivity_method', type=reflectivity_type,
                        help='algorithm for calculating reflectivity',
                        default='zoeppritz', choices=MODELS.keys())

    parser.add_argument('colour', type=str,
                        help='Matplotlib colourmap', default='Greys')

    return parser

def run_script(args):
    
    matplotlib.interactive(False)
    
    rc_series = args.rc 
            
    warray_amp = create_theta_spike(args.pad,
                                    Rprop0, Rprop1, theta,
                                    args.f, args.points,
                                    args.reflectivity_method)
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    plt.gray()
    aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]
    ax1.imshow(warray_amp, aspect=aspect, cmap=args.colour)
    
    plt.title(args.title % locals())
    plt.ylabel('time (ms)')
    plt.xlabel('trace')
    
    fig_path = tempfile.mktemp('.jpeg')
    plt.savefig(fig_path)
    
    with open(fig_path, 'rb') as fd:
        data = fd.read()
        
    unlink(fig_path)
        
    return data
    
    
def main():
    parser = ArgumentParser(usage=short_description,
                            description=__doc__)
    add_arguments(parser)
    args = parser.parse_args()
    run_script(args)
    
if __name__ == '__main__':
    main()
