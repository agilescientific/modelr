'''
Created on Apr 30, 2012

@author: sean
'''
from argparse import ArgumentParser
from modelr.zoep_calc import zoeppritz
from modelr.wavelet import ricker_freq

short_description = 'Create an ...'

#import matplotlib.mlab as mlab
import matplotlib
#from matplotlib.pyplot import figure, show
import numpy as np
#import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
import tempfile
from os import unlink
from modelr.urlargparse import URLArgumentParser
#from scipy.signal import ricker


def create_parser():
    parser = URLArgumentParser('This is the default script')
    
    parser.add_argument('title', default='Plot', type=str, help='The title of the plot')
    parser.add_argument('xlim', type=float, action='list')
    parser.add_argument('time', default=150, type=int, help='The size in mili seconds of the plot')
    
    parser.add_argument('rho0', type=float, default=.3, help='lower', required=True)
    parser.add_argument('rho1', type=float, default=.3, help='upper', required=True)

    parser.add_argument('vp0', type=float, default=.3, help='lower', required=True)
    parser.add_argument('vp1', type=float, default=.3, help='upper', required=True)

    parser.add_argument('vs0', type=float, help='lower')
    parser.add_argument('vs1', type=float, help='upper')
    
    parser.add_argument('theta', type=float, action='list', help='Angle of incidence start,stop,step')
    
    parser.add_argument('f', type=float, help='frequency', default=25)
    return parser


def run_script(args):
    
    matplotlib.interactive(False)
    
    thetas = np.arange(args.theta[0], args.theta[1], args.theta[2])
    
    array_amp = np.zeros([args.time, thetas.size])
#    array_time = np.arange(args.time)
    
    vs0 = args.vs0 if args.vp0 / 2 is None else args.vs0
    vs1 = args.vs1 if args.vp1 / 2 is None else args.vs1
    

    Rpp = zoeppritz(args.vp0, vs0, args.rho0, args.vp1, vs1, args.rho1, thetas)

    array_amp[args.time // 2, :] = Rpp
    
    r = ricker_freq(100, args.f)
    
    print 'r.shape', r.shape
    print 'array_amp', array_amp.shape
    
    warray_amp = np.zeros_like(array_amp)
    for i in range(thetas.size):
        warray_amp[:, i] = np.convolve(array_amp[:, i], r, mode='same')
    fig = plt.figure()
    
    ax1 = fig.add_subplot(111)

    ax1.imshow(warray_amp)
    print warray_amp.shape
#    ax1.plot(warray_amp, array_time)
    
    plt.title(args.title % locals())
    plt.gray()
    plt.ylabel('time (ms)')
    plt.xlabel('amplitude')
    
#    ax = plt.gca()
#    ax.set_ylim(ax.get_ylim()[::-1])
#    ax.set_xlim(args.xlim)
    
    fig_path = tempfile.mktemp('.jpeg')
    plt.savefig(fig_path)
    
    with open(fig_path, 'rb') as fd:
        data = fd.read()
        
    unlink(fig_path)
        
    return data
    
    
def main():
    parser = ArgumentParser(usage=short_description, description=__doc__)
    parser.add_argument('time', default=150, type=int, help='The size in mili seconds of the plot')
    args = parser.parse_args()
    run_script(args)
    
#    plt.show()
if __name__ == '__main__':
    main()

    v1
