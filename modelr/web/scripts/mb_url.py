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

short_description = 'Use a model from a file on the web.'

def add_arguments(parser):
    
    default_parser_list = ['ntraces',
                           'pad',
                           'reflectivity_method',
                           'title',
                           'theta',
                           'f',
                           'colourmap',
                           'wavelet',
                           'wiggle_skips',
                           'base1','base2','overlay1','overlay2',
                           'opacity'                           
                           ]
    
    default_parsers(parser,default_parser_list)
    
                        
    parser.add_argument('Rock0',
                        type=rock_properties_type, 
                        help='Rock properties of rock 0 [Vp,Vs, rho]',
                        required=True,
                        default='2350,1150,2400'
                        )
                        
    parser.add_argument('Rock1',
                        type=rock_properties_type, 
                        help='Rock properties of rock 1 [Vp, Vs, rho]',
                        required=True,
                        default='2150,1050,2300'
                        )
    
    parser.add_argument('Rock2',
                        type=rock_properties_type, 
                        help='Rock properties of rock 2 [Vp, Vs, rho]',
                        required=False,
                        default='2500,1250,2600'
                        )
    
    parser.add_argument('Rock3',
                        type=rock_properties_type, 
                        help='Rock properties of rock 3 [Vp, Vs, rho]',
                        required=False,
                        default='2600,1350,2700'
                        )
    
    parser.add_argument('url',
                        type=str, 
                        help='a URL for an image with 3 colours',
                        required=True,
                        default='http://www.subsurfwiki.org/mediawiki/images/4/41/Modelr_test_ellipse.png'
                        )
    
    parser.add_argument('rocks',
                        type=int, 
                        help='the number of rocks in the model',
                        required=False
                        )
    
    parser.add_argument('minimum',
                        type=int, 
                        help='the minimum impedance (or use Rocks)',
                        required=False
                        )
    
    parser.add_argument('maximum',
                        type=int, 
                        help='the maximum impedance (or use Rocks)',
                        required=False
                        )
    
    return parser


def run_script(args):
    
    matplotlib.interactive(False)
 
    Rprop0 = args.Rock0 
    Rprop1 = args.Rock1
    Rprop2 = args.Rock2
    Rprop3 = args.Rock3
    
    colourmap = {}

    if isinstance(Rprop0, str):
        Rprop0 = None
    else:
        colourmap[0] = Rprop0 
        
    if isinstance(Rprop1, str):
        Rprop1 = None
    else:
        colourmap[1] = Rprop1 
        
    if isinstance(Rprop2, str):
        Rprop2 = None
    else:
        colourmap[2] = Rprop2 
        
    if isinstance(Rprop3, str):
        Rprop3 = None
    else:
        colourmap[3] = Rprop3 
        
    method = args.reflectivity_method
    
    if not isinstance(args.rocks, int):
        colours = 0
    else:
        colours = args.rocks

    model = mb.web2array(args.url,
                         colours = colours,
                         minimum = args.minimum,
                         maximum = args.maximum
                         )

    reflectivity = get_reflectivity(data = model,
                                    colourmap = colourmap,
                                    theta = args.theta,
                                    reflectivity_method = method
                                    )

    warray_amp = do_convolve(args.wavelet, args.f, reflectivity, traces=args.ntraces)

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
                           cmap = args.colourmap,
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
                if plot.index(layer) == 0:
                    # then we're in an base layer so...
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
