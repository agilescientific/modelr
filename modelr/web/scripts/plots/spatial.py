'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import h5py

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from argparse import ArgumentParser


from modelr.web.util import get_figure_data

import modelr.modelbuilder as mb
from modelr.web.defaults import default_parsers
from svgwrite import rgb

short_description = ('Look at plots '
                     'across spatial, offset, and frequency '
                     'cross-sections')


def add_arguments(parser):


    parser.add_argument('theta',
                        type=float,
                        default=0.0,
                        help="Offset angle",
                        interface='slider',
                        range=[0,45])
    
                        
    parser.add_argument('trace',
                        type=int,
                        help='Trace',
                        default=25,
                        interface='slider',
                        range=[0,1000]
                        )

    

    return parser

def run_script(earth_model,
               seismic_model,
               args):

    fig =plt.figure()
    gs = gridspec.GridSpec(1, 2,width_ratios=[4,1])
    axarr = [plt.subplot(gs[0]), plt.subplot(gs[1])]

    
    seismic_model.go(earth_model,
                     theta=args.theta)
    seismic_data = seismic_model.seismic

    t = seismic_model.dt * np.arange(seismic_data.shape[0])
    
    axarr[0].imshow(seismic_data[:,:, 0, 0],aspect='auto',
                    extent=[0, seismic_data.shape[1],
                            t[-1], t[0]],
                    cmap='Greys')
    axarr[0].axvline(x=args.trace, lw=3, color='b')
    axarr[0].set_title('spatial cross-section')

    axarr[1].plot(seismic_data[:,args.trace,0,0],t)
    
    plt.gca().invert_yaxis()
    axarr[1].axis('tight')

    fig.tight_layout()

    # set the frequency options (need to do this more elegantly)
    seismic_model.f = np.arange(0,50)

    return get_figure_data()
        
    

    
if __name__ == '__main__':
    main()
