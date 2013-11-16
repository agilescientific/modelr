from argparse import ArgumentParser
import matplotlib
import matplotlib.pyplot as plt
from modelr.web.urlargparse import rock_properties_type,\
     reflectivity_func
from modelr.rock_properties import FUNCTIONS
from modelr.web.util import return_current_figure
import numpy as np
from scipy import arcsin


short_description = (
    "Make a stochastic avo plot using monte carlo simulation around the rock property uncertainties."
    )

def add_arguments(parser):

    parser.add_argument('title', default='Plot',
                        type=str, help='The title of the plot')

    parser.add_argument('Rpp0', type=rock_properties_type, 
                        help='rock properties of upper rock: Vp, Rho, Vs, Vp std. dev., Rho std. dev., Vs std. dev.)',
                        required=True)
    
    parser.add_argument('Rpp1', type=rock_properties_type, 
                        help='rock properties of lower rock: Vp, Rho, Vs, Vp std. dev., Rho std. dev., Vs std. dev.',
                        required=True)
                        
    parser.add_argument( 'iterations', type=int, default=1000, 
                         help='number of monte carlo simulations' )
    
    parser.add_argument('reflectivity_method', type=reflectivity_func,
                        help='Algorithm for calculating reflectivity',
                        default='zoeppritz',
                        choices=FUNCTIONS.keys())
                        
    parser.add_argument('plot_type', type=str,
                        help='AVO, AB, or dashboard ',
                        default='AVO'
                        )
    
    
    
 
    return parser

def run_script(args):
    
    matplotlib.interactive(False)
 
    Rprop0 = args.Rpp0 
    Rprop1 = args.Rpp1

    theta = np.arange(0,90)
    
    if args.plot_type == 'dashboard':
        
        fig =plt.figure()
        fig.subplots_adjust(bottom=0.025, left=0.025, top = 0.975, right=0.975)

        plt.subplot(1,2,1)
        plt.xticks([]), plt.yticks([])
        
        plt.subplot(1,2,2)
        plt.xticks([]), plt.yticks([])
        
        plt.subplot(2,3,4)
        plt.xticks([]), plt.yticks([])
        
        plt.subplot(2,3,5)
        plt.xticks([]), plt.yticks([])
        
        plt.subplot(2,3,6)
        plt.xticks([]), plt.yticks([])
        
    else: 
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
        if args.plot_type == 'AVO':        
            plt.plot( theta, reflect ,color = 'red', alpha = 0.02)
            if vp1 > vp0:
                theta_crit = arcsin( vp0 / vp1 )*180/np.pi
                plt.axvline( x= theta_crit , color='black',alpha=0.02 )
            plt.ylim((-1,1))
            data += np.nan_to_num( reflect )        
                   
        else:
            plt.scatter( reflect[0], (reflect[60]-reflect[0] ) , color = 'red' , s=20, alpha=0.05 )
            data += np.nan_to_num( reflect )   
          
    data /= args.iterations
    
    if args.plot_type == 'AVO':
        
        plt.plot( theta, data, color='green' )
        
        plt.title(args.title % locals())
        plt.ylabel('reflectivity')
        plt.ylim(-1,1)
        plt.xlabel('offset (degrees)')
        plt.grid()
        
    else:    
        #don't have the 
        plt.scatter( data[0], data[60]-data[0] , color='green', s=40, alpha = 0.5 ) 
        
        plt.title(args.title % locals())
        plt.ylabel('gradient [B]')
        plt.ylim(-1,1)
        plt.xlabel('intercept [A]')
        plt.xlim(-1,1)
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
