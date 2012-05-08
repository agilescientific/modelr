'''
Created on Apr 30, 2012

@author: sean
'''
from argparse import ArgumentParser
from modelr.wavelet import ricker_freq
from modelr.rock_properties import MODELS
from os import unlink
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import tempfile
from modelr.web.urlargparse import rock_properties_type, reflectivity_type
from modelr.web.util import return_current_figure

short_description = 'Create an ...'

def add_arguments(parser):
    
    parser.add_argument('title', default='Plot', type=str, help='The title of the plot')
    parser.add_argument('xlim', type=float, action='list', help='The range of amplitudes to plot eg. xlim=-1.0,1.0')
    parser.add_argument('time', default=150, type=int, help='The size in Mili seconds of the plot')
    
    parser.add_argument('Rpp0', type=rock_properties_type, help='rock properties of upper rock', required=True)
    parser.add_argument('Rpp1', type=rock_properties_type, help='rock properties of lower rock', required=True)
    
    parser.add_argument('theta1', type=float, help='angle of incidence')
    
    parser.add_argument('f', type=float, help='frequency', default=25)
    parser.add_argument('reflectivity_model', type=reflectivity_type, help='... ', default='zoeppritz', choices=MODELS.keys())
    return parser


def run_script(args):
    
    matplotlib.interactive(False)
    
    array_amp = np.zeros([args.time])
    array_time = np.arange(args.time)
    
    Rpp = args.reflectivity_model(args.Rpp0, args.Rpp1, args.theta1)
    
    array_amp[args.time // 2] = Rpp
    
    r = ricker_freq(100, args.f)
    
    warray_amp = np.convolve(array_amp, r, mode='same')
    
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
    parser.add_argument('time', default=150, type=int, help='The size in mili seconds of the plot')
    args = parser.parse_args()
    run_script(args)
    
#    plt.show()
if __name__ == '__main__':
    main()

