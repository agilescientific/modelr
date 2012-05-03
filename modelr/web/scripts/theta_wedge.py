'''
Created on Apr 30, 2012

@author: sean
'''
from argparse import ArgumentParser
from modelr.reflectivity import create_theta
from modelr.rock_properties import zoeppritz
from modelr.web.urlargparse import rock_properties_type
from modelr.web.util import return_current_figure
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

short_description = 'Create an wedge model ...'

def add_arguments(parser):
    
    parser.add_argument('title', default='Plot', type=str, help='The title of the plot')

    parser.add_argument('pad', default=50, type=int, help='The time in mili seconds aboe and below the wedge')
    parser.add_argument('thickness', default=50, type=int, help='The maximum thickness of the wedge')
    
    parser.add_argument('Rpp0', type=rock_properties_type, help='rock properties of upper rock', required=True)
    parser.add_argument('Rpp1', type=rock_properties_type, help='rock properties of lower rock', required=True)
    
    parser.add_argument('theta', type=float, action='list', help='Angle of incidence')
    
    parser.add_argument('f', type=float, help='frequency', default=25)
    parser.add_argument('points', type=int, help='choose ... ', default=100)
    parser.add_argument('reflectivity_method', type=str, help='choose ... ', default='zoeppritz')
    return parser

methods = {'zoeppritz': zoeppritz,
           'const': lambda r1, r2, theta: 0.3}

def run_script(args):
    
    matplotlib.interactive(False)
    
    Rprop0 = args.Rpp0 
    Rprop1 = args.Rpp1
    
    theta = np.arange(args.theta[0], args.theta[1], args.theta[2])
    
    reflectivity_method = methods[args.reflectivity_method]
    
    warray_amp = create_theta(args.pad, args.thickness,
                              Rprop0, Rprop1, theta, args.f, args.points, reflectivity_method)
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    plt.gray()
    aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]
    ax1.imshow(warray_amp, aspect=aspect)
    
    plt.title(args.title % locals())
    plt.ylabel('time (ms)')
    plt.xlabel('trace')
    
    return return_current_figure()    
    
def main():
    parser = ArgumentParser(usage=short_description, description=__doc__)
    add_arguments(parser)
    args = parser.parse_args()
    run_script(args)
    
if __name__ == '__main__':
    main()
