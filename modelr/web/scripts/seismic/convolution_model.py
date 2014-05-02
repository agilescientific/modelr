'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.web.urlargparse import  wavelet_type

from modelr.constants import WAVELETS 

from modelr.web.defaults import default_parsers


from modelr.reflectivity import do_convolve

short_description = ("Do a convolution seismic model across spatial, angle, and wavelet domains")


def add_arguments(parser):

    
    parser.add_argument('wavelet',
                        type=wavelet_type,
                        help='Wavelet',
                        default='ricker',
                        choices=WAVELETS.keys())
    
    parser.add_argument('f', type=float, default=15.0,
                        help="frequency",
                        interface='slider',
                        range=[8,100])
    
    parser.add_argument('phase', type=float, default=15.0,
                        help="phase",
                        interface='slider',
                        range=[0,180])

    """parser.add_argument('f2', type=float, default=15.0,
                        help="Last center frequency of the wavelet bank")
    parser.add_argument('f_res', type=str, default="octave",
                        choices=["linear", "octave"],
                        help="Wavelet bank resolution")
    """

    """
    parser.add_argument('theta1', type=float, default=0.0,
                       help="First offset angle of the experiment")
    parser.add_argument('theta2', type=float, default=0.0,
                        help="Last offset angle of the experiment")
    parser.add_argument('stack', type=int, default=1,
                        help="Number of offset measurements")
    """
    """
    parser.add_argument("sensor_spacing", type=float, default=1,
                        help="Spacing of the sensors")
    parser.add_argument("dt", type=float, default=0.001,
                        help="Sampling rate of the experiment")
    """
 
    return parser

def run_script(earth_model, seismic_model, theta=None,
               traces=None):

    if earth_model.reflectivity() is None:

        if earth_model.units == "depth":
            earth_model.depth2time(seismic_model.dt)

        earth_model.update_reflectivity(seismic_model.offset_angles(),
                                        seismic_model.n_sensors)

        
    
    wavelets = seismic_model.wavelets()


    seismic = do_convolve(wavelets,
                          earth_model.reflectivity(theta=theta),
                          traces=traces,
                          theta=theta)

    return seismic
