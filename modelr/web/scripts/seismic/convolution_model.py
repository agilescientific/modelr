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
from agilegeo.util import noise_db, rms
from modelr.reflectivity import do_convolve

short_description = ("Convolution model with synthetic wavelets")


def add_arguments(parser):
    
    parser.add_argument('f', type=float, default=12,
                        help="Frequency",
                        interface='slider',
                        range=[0,1000])
    
    parser.add_argument('phase', type=float, default=0.0,
                        help="Phase",
                        interface='slider',
                        range=[-180,180])

    parser.add_argument('snr', type=float, default=900,
                        help="Signal:noise (dB)",
                        interface='slider',
                        range=[0,1000])
    
    parser.add_argument('wavelet',
                        type=wavelet_type,
                        help='Wavelet',
                        default='ricker',
                        choices=WAVELETS.keys())

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
               traces=None, snr=50):

    if earth_model.reflectivity() is None:

        if earth_model.units == "depth":
            earth_model.depth2time(seismic_model.dt,
                                   samples=seismic_model.n_sensors)

        else:
            earth_model.resample(seismic_model.dt)

        earth_model.update_reflectivity(seismic_model.offset_angles(),
                                        seismic_model.n_sensors)


    snr_scale = np.linspace(-50,50,1000)
    wavelets = seismic_model.wavelets()

    ref = earth_model.reflectivity(theta=theta)
    
    noise = noise_db(ref, snr_scale[snr])

    
    ref += noise

    seismic = do_convolve(wavelets,
                          ref,
                          traces=traces,
                          theta=theta)

    return seismic
