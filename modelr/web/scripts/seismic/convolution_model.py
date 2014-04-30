'''
Created on Apr 30, 2012

@author: Sean Ross-Ross, Matt Hall, Evan Bianco
'''
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from argparse import ArgumentParser

from modelr.web.urlargparse import  wavelet_type, reflectivity_type

from modelr.web.util import modelr_plot
from modelr.constants import WAVELETS, REFLECTION_MODELS 
import modelr.modelbuilder as mb
from modelr.web.defaults import default_parsers
from svgwrite import rgb


from modelr.reflectivity import get_reflectivity, do_convolve

short_description = ("Do a convolution seismic model across spatial, angle, and wavelet domains")


def add_arguments(parser):

    

    """parser.add_argument('f1', type=float, default=15.0,
                        help="First center frequency of the wavelet bank")
    parser.add_argument('f2', type=float, default=15.0,
                        help="Last center frequency of the wavelet bank")
    parser.add_argument('f_res', type=str, default="octave",
                        choices=["linear", "octave"],
                        help="Wavelet bank resolution")
    """
    parser.add_argument('wavelet',
                            type=wavelet_type,
                            help='Wavelet type',
                            default='ricker',
                            choices=WAVELETS.keys()
                            )
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
    parser.add_argument('reflectivity_method',
                            type=reflectivity_type,
                            help='Reflectivity Algorithm',
                            default='zoeppritz',
                            choices=REFLECTION_MODELS.keys()
                            ) 
 
    return parser

def run_script(earth_model, seismic_model):


    # convert to time
    if earth_model.units == 'depth':
        earth_model.depth2time(seismic_model.dt)

    # get the sensor locations
    # spacing = seismic_model.sensor_spacing
    length = earth_model.length
    samples = np.linspace(0, length, seismic_model.n_sensors,
                          endpoint=True)
    
    
    reflectivity = \
          get_reflectivity(data=earth_model.get_data(samples=samples),
                           colourmap=earth_model.property_map,
                           theta=seismic_model.offset_angles(),
                           reflectivity_method=seismic_model.reflectivity_method)

    
    seismic = do_convolve(seismic_model.wavelets(), reflectivity)

    return seismic, reflectivity
