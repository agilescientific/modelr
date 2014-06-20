'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib
from scipy.interpolate import interp1d

import urllib2
import matplotlib.pyplot as plt

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers
from modelr.web.urlargparse import rock_properties_type,\
     earth_model_type
from modelr.constants import dt
from agilegeo.avo import zoeppritz

from modelr.web.util import modelr_plot
from agilegeo.wavelet import ricker

import modelr.modelbuilder as mb

from svgwrite import rgb
from StringIO import StringIO

from PIL import Image
short_description = 'Spatial view of an image-based model'

def add_arguments(parser):
    
    default_parser_list = [
                           'base1','base2','overlay1','overlay2',
                           'opacity', 'colourmap','f','theta'
                           ]
    
    default_parsers(parser,default_parser_list)
    
    parser.add_argument('model',
                        type=earth_model_type, 
                        help='earth model',
                        required=True
                        )
                        
    parser.add_argument('twt_range',
                        type=float, 
                        action='list', 
                        help='Range of two-way-time [ms] for earth model',
                        required=True,
                        default='0,1000'
                        )
                        
    parser.add_argument('wiggle_skips',
                        type=int,
                        help='number of traces to skip in display',
                        required = True, 
                        default = 10,
                        )

    parser.add_argument('tslice',
                        type=float, 
                        help='time [ms] along which to plot instantaneous amplitude ',
                        required=True,
                        default=150
                        )
                      
    parser.add_argument('scale',
                        type=float,
                        action='list', 
                        help='0 for auto scale, and (optional) clip percentile (e.g. 99)',
                        required=True,
                        default='1.0,99'
                        )
                        
    parser.add_argument('aspect_ratio',
                        type=float,
                        help='vertical stretch for output dimensions, < 1 = squash, > 1 = stretch',
                        required=True,
                        default='1.0'
                        )
                        
    parser.add_argument('fs',
                        type=int,
                        help='fontsize',
                        required=True,
                        default='10'
                        )

    return parser


def run_script(args):
    
    matplotlib.interactive(False)

    args.reflectivity_method = zoeppritz
    args.title = 'Forward model - spatial cross section'
    args.wavelet = ricker
    args.margin=1
    args.slice='spatial'
    args.trace = 0
    
    model = urllib2.urlopen(args.model["image"]).read()
    model = Image.open(StringIO(model)).convert("RGB")
    model = np.asarray(model)
    
    # decimate the first dimension of the model (into sample rate: dt [ms])
    
    ds = float(args.twt_range[1] - args.twt_range[0]) / float(model.shape[0])
    

    
    x = (np.arange(0, model.shape[0]) * ds) + args.twt_range[0] 
    

    f = interp1d(x, model.astype("float"), axis=0, kind="nearest")


    
    xnew = np.arange(args.twt_range[0],args.twt_range[1], dt * 1000.0)

    xnew = xnew[np.where(xnew < np.amax(x))] 
    
    
    model_new = f(xnew)
    
    mapping = args.model["mapping"]

    for colour in mapping:
        rock = rock_properties_type(mapping[colour]["property"])
        mapping[colour] = rock

    args.ntraces =  model_new.shape[1]
                                             
    return modelr_plot(model_new, mapping, args)
 
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

