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

from modelr.web.util import wiggle
from modelr.web.util import get_figure_data

from modelr.reflectivity import get_reflectivity, do_convolve
import modelr.modelbuilder as mb

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
                           'colourmap',
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
                        
    parser.add_argument('wiggle_skips',
                        type=int,
                        help='Wiggle traces to skip',
                        default=0
                        )
                                                
    parser.add_argument('base1',
                        type=str,
                        help='Plot 1, base layer',
                        choices=['wiggle', 'variable-density', 'earth-model', 'reflectivity'],
                        default='variable-density'
                        )
    
    parser.add_argument('overlay1',
                        type=str,
                        help='Plot 1, overlay',
                        choices=['none', 'wiggle', 'variable-density', 'earth-model', 'reflectivity'],
                        default='none'
                        )
    
    parser.add_argument('base2',
                        type=str,
                        help='Plot 2, base layer',
                        choices=['none', 'wiggle', 'variable-density', 'earth-model', 'reflectivity'],
                        default='none'
                        )
    
    parser.add_argument('overlay2',
                        type=str,
                        help='Plot 2, overlay',
                        choices=['none', 'wiggle', 'variable-density', 'earth-model', 'reflectivity'],
                        default='none'
                        )
    
    parser.add_argument('opacity',
                        type=float,
                        help='Opacity of overlays',
                        default=0.5
                        )
 
    parser.add_argument('transparent',
                        type=str,
                        help='plot background transparency',
                        default='True'
                        options=['True','False']
                        )
 
    return parser

def run_script(args):
    
    matplotlib.interactive(False)
    
    if args.transparent == 'False' or args.transparent = 'No':
        transparent = False
    else:
        transparent = True
    
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
                                    reflectivity_method = args.reflectivity_method
                                    )
    
    # Get the seismic array
    warray_amp = do_convolve(args.wavelet, args.f, reflectivity)
    
    nsamps, ntraces = model.shape
    dt = 0.001 #sample rate of model (has to match wavelet)
    dx = 10    #trace offset (in metres)
    
    #################################
    # Build the plot(s)
       
    # Simplify the plot request a bit
    # This will need to be a loop if we want to cope with
    # an arbitrary number of base plots; or allow up to 6 (say)
    base1 = args.base1
    
    if args.overlay1 == 'none':
        overlay1 = None
    else:
        overlay1 = args.overlay1
    
    if args.base2 == 'none':
        base2 = None
    else:
        base2 = args.base2
    
    if args.overlay2 == 'none':
        overlay2 = None
    else:
        overlay2 = args.overlay2
    
    plots = [(base1, overlay1), (base2, overlay2)]

    # Calculate some basic stuff
    aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]                                        
    pad = np.ceil((warray_amp.shape[0] - model.shape[0]) / 2)

    # Work out the size of the figure
    each_width = 5
    width = each_width*len(plots)
    height = width/aspect

    # First, set up the matplotlib figure
    fig = plt.figure(figsize=(width, height))
        
    # Start a loop for the figures...
    for plot in plots:
        
        # If there's no base plot for this plot,
        # then there are no more plots and we're done
        if not plot[0]:
            break
            
        # Establish what sort of subplot grid we need
        l = len(plots)
        p = plots.index(plot)
                
        # Set up the plot 'canvas'
        ax = fig.add_subplot(1,l,p+1)
            
        # Each plot can have two layers (maybe more later?)
        # Display the two layers by looping over the non-blank elements
        # of the tuple
        for layer in filter(None, plot):
            
            # for starters, find out if this is a base or an overlay
            if plot.index(layer) == 1:
                # then we're in an overlay so...
                alpha = args.opacity
            else:
                alpha = 1.0
            
            # Now find out what sort of plot we're making on this loop...        
            if layer == 'earth-model':
                ax.imshow(model,
                           cmap = plt.get_cmap('gist_earth'),
                           vmin = np.amin(model)-np.amax(model)/2,
                           vmax = np.amax(model)+np.amax(model)/2,
                           alpha = alpha,
                           aspect='auto',
                           extent=[0,model.shape[1],model.shape[0]*dt,0],
                           origin = 'upper'  
                           )
            
            elif layer == 'variable-density':
                ax.imshow(warray_amp[pad:-pad,:],
                           cmap = args.colourmap,
                           alpha = alpha,
                           aspect='auto',
                           extent=[0,model.shape[1],model.shape[0]*dt,0], 
                           origin = 'upper'
                           )
    
            elif layer == 'reflectivity':
                # Show unconvolved reflectivities
                ax.imshow(reflectivity,
                           cmap = plt.get_cmap('Greys'),
                           aspect='auto',
                           extent=[0,model.shape[1],model.shape[0]*dt,0],
                           origin = 'upper' 
                           )

            elif layer == 'wiggle':
            # wiggle needs an alpha setting too
                wiggle(warray_amp[pad:-pad,:],
                       dt = dt,
                       skipt = args.wiggle_skips,
                       gain = args.wiggle_skips + 1,
                       line_colour = 'black',
                       fill_colour = 'black',
                       opacity = 0.5
                       )    
                if plot.index(layer) == 0:
                    # then we're in an base layer so...
                    ax.set_ylim(max(ax.set_ylim()),min(ax.set_ylim()))

            else:
                # We should never get here
                continue     
        ax.set_xlabel('trace')
        ax.set_ylabel('time [s]')
        ax.set_title(args.title % locals())
        
    fig.tight_layout()

    return get_figure_data(transparent=transparent)
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