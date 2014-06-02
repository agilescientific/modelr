'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import urllib2
import matplotlib.pyplot as plt

from argparse import ArgumentParser
from modelr.web.defaults import default_parsers
from modelr.web.urlargparse import rock_properties_type,\
     earth_model_type
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
                        
    


    parser.add_argument('tslice',
                        type=float, 
                        help='time [s] along which to plot instantaneous amplitude ',
                        required=True,
                        default=0.150
                        )
                      
    parser.add_argument('scale',
                        type=float,
                        action='list', 
                        help='0 for auto scale, and (optional) clip percentile (e.g. 99)',
                        required=True,
                        default='1.0,99'
                        )

    return parser


def run_script(args):
    
    matplotlib.interactive(False)

    args.reflectivity_method = zoeppritz
    args.title = 'Forward model - spatial cross section'
    args.wavelet = ricker
    args.wiggle_skips = 10
    args.aspect_ratio = 1
    args.margin=1
    args.slice='spatial'
    args.trace = 0
    
    model = urllib2.urlopen(args.model["image"]).read()
    model = Image.open(StringIO(model)).convert("RGB")
    model = np.asarray(model)
    
    mapping = args.model["mapping"]

    for colour in mapping:
        rock = rock_properties_type(mapping[colour]["property"])
        mapping[colour] = rock

    args.ntraces =  model.shape[1]
                                             
    return modelr_plot(model, mapping, args)

    
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

