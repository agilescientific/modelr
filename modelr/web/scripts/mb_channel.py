'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers

from modelr.reflectivity import get_reflectivity, do_convolve

import modelr.modelbuilder as mb

from modelr.web.urlargparse import rock_properties_type
from modelr.web.util import return_current_figure
from modelr.web.util import wiggle

# This is required for Script help
short_description = 'Create a simple wedge model.'

def add_arguments(parser):
    
    default_parser_list = ['ntraces',
                           'pad',
                           'reflectivity_method',
                           'title',
                           'theta',
                           'f',
                           'display',
                           'colour',
                           'wavelet'
                           ]
    
    default_parsers(parser,default_parser_list)
                            
    parser.add_argument('thickness',
                        default=50,
                        type=int,
                        help='The maximum thickness of the wedge'
                        )
                            
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Rock properties of upper rock [Vp,Vs, rho]',
                        required=True,
                        default='2400,1200,2500'
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
                        default='2500,1250,2650'
                        )
    
    parser.add_argument('wiggle_skips',
                        type=int,
                        help='Wiggle traces to skip',
                        default=0
                        )
                        
    parser.add_argument('panels',
                        type=str,
                        help='The plot(s) to return',
                        default='seismic',
                        choices= ['earth-model','seismic','both']
                        )
                        
    parser.add_argument('model_wiggle',
                        type=str,
                        help='Plot wiggles on model plot',
                        default='False',
                        choices=['True','False']
                        )
                        
    return parser

def run_script(args):
    
    matplotlib.interactive(False)
    
    model_wiggle = bool(args.model_wiggle)

    # Get the physical model (an array of rocks)    
    model = mb.channel(pad = args.pad,
                   thickness = args.thickness,
                   traces = args.ntraces,
                   layers = (args.Rock0,args.Rock1,args.Rock2)
                   )

    colourmap = { 0: args.Rock0, 1: args.Rock1 }
    if not isinstance(args.Rock2, str):
        colourmap[2] = args.Rock2
    
    reflectivity = get_reflectivity(data = model,
                                    colourmap = colourmap,
                                    theta = args.theta,
                                    f = args.f,
                                    reflectivity_method = args.reflectivity_method
                                    )
    
    # Get the seismic array
    warray_amp = do_convolve(args.wavelet, args.f, reflectivity)
    
    #################################
    # Build the plot
    aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]                                        
    
    pad = np.ceil((warray_amp.shape[0] - model.shape[0]) / 2)

    if args.panels == 'both':
        fig = plt.figure(figsize = (10,3))
        ax1 = fig.add_subplot(121)
        ax1.imshow( model,aspect=aspect, cmap=plt.get_cmap('gist_earth'),vmin=np.amin(model)-np.amax(model)/2,vmax= np.amax(model)+np.amax(model)/2)
        
        if model_wiggle:
            wiggle(warray_amp[pad:-pad,:], dt=1, skipt = args.wiggle_skips, gain = args.wiggle_skips+1 )
            ax1.set_ylim(max(ax1.set_ylim()),min(ax1.set_ylim()))
        
        ax1.set_xlabel('trace')
        ax1.set_ylabel('time [ms]')
        #put colorbar here
        
        ax2 = fig.add_subplot(122)
        
        if args.display == 'wiggle':        
            wiggle(warray_amp, dt=1, skipt = args.wiggle_skips, gain = args.wiggle_skips+1 )
            ax2.set_xlabel('trace')
            ax2.set_ylabel('time [ms]')
                   
        else:
            ax2 = fig.add_subplot(122)
            ax2.imshow( warray_amp, aspect=aspect, cmap=args.colour)
            ax2.set_ylim(max(ax2.set_ylim()),min(ax2.set_ylim()))
        
        if args.display == 'both':
            ax2 = fig.add_subplot(122)
            wiggle(warray_amp, dt=1, skipt = args.wiggle_skips, gain = args.wiggle_skips+1 )
            #invert y-axis
            ax2.set_ylim(max(ax2.set_ylim()),min(ax2.set_ylim()))
            ax2.set_xlabel('trace')
            ax2.set_ylabel('time [ms]')
        
    if args.panels == 'earth-model':    
        fig = plt.figure()
        ax1 = fig.add_subplot(111)  
        ax1.imshow( model , aspect=aspect, cmap=plt.get_cmap('gist_earth'), vmin=np.amin(model)-np.amax(model)/2,vmax= np.amax(model)+np.amax(model)/2 )
        ax1.set_xlabel('trace')
        ax1.set_ylabel('time [ms]')
        ax1.set_title(args.title % locals()) 
    
    if args.panels == 'seismic':
        fig = plt.figure() 
        
        if args.display == 'wiggle':        
            ax1 = fig.add_subplot(111)
            wiggle(warray_amp, dt=1, skipt = args.wiggle_skips, gain = args.wiggle_skips+1)       
        else:
            ax1 = fig.add_subplot(111)
            ax1.imshow( warray_amp, aspect=aspect, cmap=args.colour)
            ax1.set_ylim(max(ax1.set_ylim()),min(ax1.set_ylim()))
        
        if args.display == 'both':
            ax1 = fig.add_subplot(111)
            wiggle(warray_amp,dt=1, skipt = args.wiggle_skips, gain = args.wiggle_skips+1 )
            #invert y-axis
            ax1.set_ylim(max(ax1.set_ylim()),min(ax1.set_ylim()))
        
        ax1.set_xlabel('trace')
        ax1.set_ylabel('time [ms]')
        #invert y-axis
        #ax1.set_ylim(max(ax1.set_ylim()),min(ax1.set_ylim()))
        ax1.set_title(args.title % locals())
    
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