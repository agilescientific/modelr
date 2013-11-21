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

short_description = 'The Agile logo!'

def add_arguments(parser):
    
    default_parser_list = ['ntraces',
                           'pad',
                           'reflectivity_method',
                           'title',
                           'theta',
                           'f',
                           'colour',
                           'wavelet'
                           ]
    
    default_parsers(parser,default_parser_list)
    
                        
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Rock properties of background [Vp,Vs, rho]',
                        required=True,
                        default='2350,1150,2400'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                        help='Rock properties of star [Vp, Vs, rho]',
                        required=True,
                        default='2150,1050,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                        help='Rock properties of Agile [Vp, Vs, rho]',
                        required=False,
                        default='2500,1250,2600'
                        )
    
    parser.add_argument('url',
                        type=str, 
                        help='a URL for an image with 3 colours',
                        required=True
                        )
    
    return parser


def run_script(args):
    
    matplotlib.interactive(False)
 
    Rprop0 = args.Rock0 
    Rprop1 = args.Rock1
    Rprop2 = args.Rock2
    
    if isinstance(Rprop2, str):
        Rprop2 = None
    
    model = mb.web2array(args.url)

    colourmap = { 0: Rprop0, 1: Rprop1, 2: Rprop2 }
        
    reflectivity = get_reflectivity(data=model,
                                    colourmap = colourmap,
                                    theta = args.theta,
                                    f = args.f,
                                    reflectivity_method = \
                                      args.reflectivity_method
                                    )
    
    warray_amp = do_convolve(args.wavelet, args.f, reflectivity)
    
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
    width = 10
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
                           aspect = aspect,
                           cmap = plt.get_cmap('gist_earth'),
                           vmin = np.amin(model)-np.amax(model)/2,
                           vmax = np.amax(model)+np.amax(model)/2,
                           alpha = alpha
                           )
            
            elif layer == 'variable-density':
                ax.imshow(warray_amp[pad:-pad,:],
                           aspect = aspect,
                           cmap = args.colour,
                           alpha = alpha
                           )
    
            elif layer == 'reflectivity':
                # Show unconvolved reflectivities
                ax.imshow(reflectivity,
                           aspect = aspect,
                           cmap = plt.get_cmap('Greys'),
                           alpha = alpha
                           )

            elif layer == 'wiggle':
                wiggle(warray_amp[pad:-pad,:],
                       dt = 1, # Not sure what this is for?
                       skipt = args.wiggle_skips,
                       gain = args.wiggle_skips + 1,
                       line_colour = 'black',
                       fill_colour = 'black',
                       opacity = 0.5
                       )
                ax.set_ylim(max(ax.set_ylim()),min(ax.set_ylim()))

            else:
                # We should never get here
                continue
        
        ax.set_xlabel('trace')
        ax.set_ylabel('time [ms]')
        ax.set_title(args.title % locals())

    fig.tight_layout()

    return get_figure_data()
    
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
