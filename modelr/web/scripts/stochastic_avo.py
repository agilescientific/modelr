from argparse import ArgumentParser
import matplotlib
import matplotlib.pyplot as plt
from modelr.web.urlargparse import rock_properties_type,\
     reflectivity_func
from modelr.rock_properties import FUNCTIONS
from modelr.web.util import return_current_figure
import numpy as np


short_description = (
    "Make a stochastic avo plot using monte carlo simulation around the rock property uncertainties."
    )

def add_arguments(parser):

    parser.add_argument('title', default='Plot',
                        type=str, help='The title of the plot')

    parser.add_argument('Rpp0', type=rock_properties_type, 
                        help='rock properties of upper rock',
                        required=True)
    
    parser.add_argument('Rpp1', type=rock_properties_type, 
                        help='rock properties of lower rock',
                        required=True)
    parser.add_argument( 'iterations', type=int, default=1000,
                         help='number of monte carlo simulations' )
    
    parser.add_argument('reflectivity_method', type=reflectivity_func,
                        help='Algorithm for calculating reflectivity',
                        default='zoeppritz',
                        choices=FUNCTIONS.keys())  
 
    return parser

def run_script(args):
    
    matplotlib.interactive(False)
 
    Rprop0 = args.Rpp0 
    Rprop1 = args.Rpp1

    theta = np.arange(0,90)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    data = np.zeros( theta.shape )
    
    for i in range( args.iterations - 1 ):

        vp0 = np.random.normal( Rprop0.vp, Rprop0.vp_sig )
        vs0 = np.random.normal( Rprop0.vs, Rprop0.vs_sig )
        rho0 = np.random.normal( Rprop0.rho, Rprop0.rho_sig )

        vp1 = np.random.normal( Rprop1.vp, Rprop1.vp_sig )
        vs1 = np.random.normal( Rprop1.vs, Rprop1.vs_sig )
        rho1 = np.random.normal( Rprop1.rho, Rprop1.rho_sig )
        
        reflect = args.reflectivity_method( vp0, vs0, rho0,
                                            vp1, vs1, rho1,
                                            theta )

        plt.plot( theta, reflect ,color = 'red', alpha = 0.02)
        data += np.nan_to_num( reflect )

    data /= args.iterations

    plt.plot( theta, data, color='green' )
    
    plt.title(args.title % locals())
    plt.ylabel('reflectivity')
    plt.ylim(-1,1)
    plt.xlabel('offset (degrees)')
    plt.grid()
    
    return return_current_figure()
    
    
def main():
    parser = ArgumentParser(usage=short_description,
                            description=__doc__)
    parser.add_argument('time', default=150, type=int, 
                        help='The size in milliseconds of the plot')
    args = parser.parse_args()
    run_script(args)
    
if __name__ == '__main__':
    main()
