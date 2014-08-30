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

short_description = ('Spatial cross-section')


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

    parser.add_argument('gain',
                        type=float,
                        range=[0,1000],
                        default=500,
                        interface='slider',
                        help='gain')
    

    return parser

def run_script(earth_model,
               seismic_model,
               args):
    # Hard code colormap
    cmap='seismic_r'  
    # min / max scaling for colormap and wiggles
    extr1 = 1.0 / (2.0 * args.gain / 1000.0)
    # decimate number of columns in synthetic
    dec = 5
    
    # Create figure
    fig =plt.figure(figsize=[15,10], facecolor = 'white')
    # Create two axes within figure
    gs = gridspec.GridSpec(1, 2,width_ratios=[19,1])
    axarr = [plt.subplot(gs[0]), plt.subplot(gs[1])]

    
    seismic_model.go(earth_model,
                     theta=args.theta)
                     
    seismic_data = seismic_model.seismic

    t = seismic_model.dt * np.arange(seismic_data.shape[0])

    img = seismic_data[:,:, 0, 0]

    # synthetic cross section
    im = axarr[0].imshow(img[:,::dec], 
                        aspect='auto', cmap=cmap, 
                        extent =[0, seismic_data.shape[1],
                            1000*seismic_model.dt*seismic_data.shape[0],0],
                            vmin = -extr1,
                            vmax = extr1,
                            interpolation='spline16')
                            
    axarr[0].set_xlim(left=0, right=seismic_data.shape[1])
    axarr[0].set_ylim(top=0,
                         bottom=1000*seismic_model.dt*seismic_data.shape[0])
    axarr[0].grid()
    axarr[0].axvline(x=args.trace, lw=1, color='k', alpha=0.25)
    axarr[0].set_title('spatial cross-section')
    axarr[0].set_ylabel('time [ms]')
    axarr[0].set_xlabel('trace')

    # Put colorbar legend on spatial cross section
    
    colorbar_ax = fig.add_axes([0.85,0.825,0.010,0.08])
    
    fig.colorbar(im, cax=colorbar_ax)
    colorbar_ax.invert_yaxis()
    colorbar_ax.text( 0.5, -0.1, '%3.1f' % -1,
                      transform=colorbar_ax.transAxes,
                      horizontalalignment='center',
                      verticalalignment='top')
    colorbar_ax.text(0.5, 1.1, '%3.1f' % 1,
                     transform=colorbar_ax.transAxes,
                     horizontalalignment='center')
    
    colorbar_ax.set_axis_off()

    
    # find max and min of section slice
    ampmin = np.amin(img)
    ampmax = np.amax(img)
    biggest = max(abs(ampmin),abs(ampmax))

    # Put wiggle trace on seismic cross-section
    
    trace1 = seismic_data[:,args.trace-1, 0, 0]
    tt = np.arange(seismic_data.shape[0]) * seismic_model.dt * 1000.0
    
    c = 20 # fractional denominator of cross section width
    gain1 = float(seismic_data.shape[1]/c)
    
    axarr[0].plot(args.trace  + gain1 * trace1, tt, 'k',alpha = 0.9)
    axarr[0].fill_betweenx(tt, args.trace + gain1 * trace1,
                            args.trace, 
                            gain1 * trace1 > 0.01,
                            color = 'k', alpha = 0.5)
    
    # Put wiggle in right panel
    #get y-axis limits, so can reverse y-axis of wiggle plot
    a1ymin, a1ymax = axarr[1].get_ylim()
    axarr[1].plot(trace1,tt,'k')
    axarr[1].fill_betweenx(tt, trace1, 0, 
                              trace1 > 0.01,
                              color = 'k', alpha = 0.5)
    axarr[1].axvline(x=0, lw=1, color='k', alpha=0.25)
    axarr[1].yaxis.tick_right()
    axarr[1].set_xticks([-1.0, 0, 1.0])
    #axarr[1].get_xaxis().set_visible(False)
    axarr[1].set_ylim((a1ymax, a1ymin))
    axarr[1].set_xlim((-biggest, biggest))
    axarr[1].set_ylabel('time [ms]')
    axarr[1].yaxis.set_label_position("right")
    axarr[1].grid()
    axarr[1].axis('tight')
    
    plt.gca().invert_yaxis()
    
    fig.tight_layout()

    # set the frequency options (need to do this more elegantly)
    seismic_model.f = np.arange(0,50)

    return get_figure_data()
        
    

    
if __name__ == '__main__':
    main()
