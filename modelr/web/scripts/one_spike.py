'''
Created on Apr 30, 2012

@author: sean
'''
from argparse import ArgumentParser
from modelr.rock_properties import MODELS
from os import unlink
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import tempfile
from modelr.web.urlargparse import rock_properties_type, reflectivity_type, wavelet_type
from modelr.web.urlargparse import WAVELETS
from modelr.web.util import return_current_figure
from agilegeo.wavelet import *

short_description = '1D model of single spike at any offset.'

def add_arguments(parser):
    
    parser.add_argument('title', default='Plot', type=str, help='The title of the plot')
    
    parser.add_argument('xlim', type=float, action='list', default='-0.2,0.2', help='The range of amplitudes to plot.')
    
    parser.add_argument('time', default=150, type=int, help='The size in milliseconds of the plot')
    
    parser.add_argument('Rock1', type=rock_properties_type, help='rock properties of upper rock', required=True)
    
    parser.add_argument('Rock2', type=rock_properties_type, help='rock properties of lower rock', required=True)

    parser.add_argument('theta1', type=float, help='angle of incidence', default=0)
    
    parser.add_argument('wavelet', type=wavelet_type, help='wavelet', default="ricker", choices=WAVELETS.keys())
    
    parser.add_argument('f', type=float, action='list', help='frequencies', default=25)
    
    parser.add_argument('reflectivity_model', type=reflectivity_type, help='Algorithm for calculating reflectivity', default='zoeppritz', choices=MODELS.keys())
    
    return parser


def run_script(args):
    
    matplotlib.interactive(False)
    
    array_amp = np.zeros([args.time])
    array_time = np.arange(args.time)
    
    Rpp = args.reflectivity_model(args.Rock1, args.Rock2, args.theta1)
    
    array_amp[args.time // 2] = Rpp
    
    #################
    # Wavelet frequency
    # Not very nice because different wavelets expect different inputs... need to make them all the same
    #
    f = args.f
    
    # This will only handle Ormsby or Ricker
    w = args.wavelet(args.time, dt, f)
    
    # Do the convolution
    warray_amp = np.convolve(array_amp, w, mode='same')
    
    fig = plt.figure()
    
    ax1 = fig.add_subplot(111)

    ax1.plot(warray_amp, array_time)
    
    plt.title(args.title % locals())
    plt.ylabel('time (ms)')
    plt.xlabel('amplitude')
    
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    ax.set_xlim(args.xlim)
    
    return return_current_figure()
    
    
def main():
    parser = ArgumentParser(usage=short_description, description=__doc__)
    args = parser.parse_args()
    run_script(args)
    
#    plt.show()
if __name__ == '__main__':
    main()

