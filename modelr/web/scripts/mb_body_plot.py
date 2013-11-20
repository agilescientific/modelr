'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tempfile, subprocess

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers
from modelr.web.urlargparse import rock_properties_type

from modelr.web.util import wiggle

from modelr.reflectivity import get_reflectivity, do_convolve
import modelr.modelbuilder as mb

short_description = 'Create a simple wedge or slab model.'

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
    
    parser.add_argument('left',
                        type=int,
                        action='list',
                        default='0,0',                        
                        help='The thickness on the left-hand side'
                        )
                        
    parser.add_argument('right',
                        type=int,
                        action='list',
                        default='0,50',                        
                        help='The thickness on the right-hand side'
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
    
    return parser


def run_script(args):
    
    matplotlib.interactive(False)
        
    left = (args.left[0], args.left[1])
    right = (args.right[0], args.right[1])
    
    model = mb.body(traces = args.ntraces,
                   pad = args.pad,
                   margin=args.margin,
                   left = left,
                   right = right,
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
    
    # This is for selecting the type of plot... not implemented yet
    if args.selection == 'frequency':
        warray_amp = do_convolve(args.wavelet, args.f, reflectivity)                        
    elif args.selection == 'offset':
        warray_amp = do_convolve(args.wavelet, args.f, reflectivity)
    else:
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
    file_list = []

    # Calculate some basic stuff
    aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]                                        
    pad = np.ceil((warray_amp.shape[0] - model.shape[0]) / 2)

    # We're going to make a PNG for each plot
            
    # Start a loop for the figures...
    
    for plot in plots:
        
        # First, set up the matplotlib figure
        fig = plt.figure()
        
        # If there's no base plot for this plot,
        # then there are no more plots and we're done
        if not plot[0]:
            break
                
        # Set up the plot
        ax = fig.add_subplot(111)
            
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
            # wiggle needs an alpha setting too
                wiggle(warray_amp[pad:-pad,:],
                       dt = 1,
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

        # Save the figure as a temporary PNG file
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        file_list.append(f.name)
        plt.savefig(f, format='png')

    # Combine the plots with montage
    # Create the outfile object
    outfile = tempfile.NamedTemporaryFile(suffix='.png')
    
    # Build the ImageMagick convert command
    command = ['convert', '-append']
    for file_name in file_list:
        command.append(file_name)
    command.append(outfile.name)
    
    # Run ImageMagick montage
    subprocess.call(command)

    # Grab the binary blob
    data = outfile.read()
    
    return data

# For now let's just try to get one base + overlay working
#    return return_current_figure()

    
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
