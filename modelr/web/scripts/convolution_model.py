'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.web.urlargparse import rock_properties_type

from modelr.web.util import modelr_plot

import modelr.modelbuilder as mb
from modelr.web.defaults import default_parsers
from svgwrite import rgb

short_description = ("Do a convolution seismic model across spatial, angle, and wavelet domains")


def add_arguments(parser):

    default_list = ['reflectivity_method', 'theta', 'f',
                    'wavelet']
    default_parsers(parser, default_list)

    return parser

def run_script(args):
    pass

    
if __name__ == '__main__':
    main()
