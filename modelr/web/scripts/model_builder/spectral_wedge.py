"""
Spectral wedge

Takes the parameters for a spectral wedge,
and passes them to the model builder script.

@author: Matt Hall

"""

import numpy as np
from modelr.modelbuilder import spectral_wedge

short_description = "Build a heterogeneous 3D wedge."

def add_arguments(parser):

    parser.add_argument('depth',
                        default=240,
                        type=int,
                        help="The total time in milliseconds.")

    parser.add_argument('length',
                        default=100,
                        type=int,
                        help="Number of samples in the " +
                        "x-direction. Will correspond to the number "+
                        "of 'inline' traces in a seismogram.")

    parser.add_argument('width',
                        default=100,
                        type=int,
                        help="Number of samples in the " +
                        "y-direction. Will correspond to the number "+
                        "of 'xline' traces in a seismogram.")

    parser.add_argument("subwedges",
                        default=3,
                        type=int,
                        help="The number of subwedges in the main wedge.")

def run_script(args):
    
    data = spectral_wedge(depth=args.depth,
                          length=args.length,
                          width=args.width,
                          subwedges=args.subwedges
                          )
    
    return data
