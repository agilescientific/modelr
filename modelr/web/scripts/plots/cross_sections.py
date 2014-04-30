'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.web.urlargparse import rock_properties_type

from modelr.web.util import get_figure_data

import modelr.modelbuilder as mb
from modelr.web.defaults import default_parsers
from svgwrite import rgb

short_description = ('Look at plots '
                     'across spatial, offset, and frequency '
                     'cross-sections')


def add_arguments(parser):


    parser.add_argument('f',
                        type=float,
                        default=10.0,
                        help="Wavelet CF to use for cross-sections")

    parser.add_argument('theta',
                        type=float,
                        default=20.0,
                        help="Offset angle to use for cross-sections")
    
                        
    parser.add_argument('trace',
                        type=int,
                        help='Trace to use for non-spatial cross-sections',
                        default=25
                        )

    return parser

def run_script(datafile, args):

    fig, axarr = plt.subplots(3,1)

    seismic_data = datafile["seismic"]
    
    axarr[0].imshow(seismic_data[:,:, args.theta, args.f],
                    aspect='auto')
    axarr[0].axvline(x=args.trace, lw=3, color='b')
    axarr[0].set_title('spatial cross-section')
    axarr[1].imshow(seismic_data[:, args.trace, :, args.f],
                    aspect='auto')
    axarr[1].axvline(x=args.theta, lw=3, color='b')
    axarr[1].set_title('angle cross-section')
    axarr[2].imshow(seismic_data[:,args.trace, args.theta, :],
                    aspect='auto')
    axarr[2].axvline(x=args.f, lw=3, color='b')
    axarr[2].set_title('wavelet cross-section')
    fig.tight_layout()

    return get_figure_data()
        
    

    
if __name__ == '__main__':
    main()
