from argparse import ArgumentParser
import matplotlib
import matplotlib.pyplot as plt
from modelr.web.urlargparse import rock_properties_type,\
      reflectivity_type_hack
from modelr.web.defaults import default_parsers
from modelr.reflectivity import FUNCTIONS

from modelr.web.util import get_figure_data
import numpy as np
from scipy import arcsin


short_description = (
    "Make a stochastic avo plot using monte carlo " +
    "simulation around the rock property uncertainties."
    )

def add_arguments(parser):

    default_parser_list = [
                           'title'
                           ]
    
    default_parsers(parser,default_parser_list)
                            

    parser.add_argument('Rpp0', type=rock_properties_type, 
                        help=('rock properties of upper rock: Vp, '+
                              'Rho, Vs, Vp std. dev., Rho std. dev.,'+
                              'Vs std. dev.'),
                        required=True)
    
    parser.add_argument('Rpp1', type=rock_properties_type, 
                        help=('rock properties of lower rock: Vp, ' +
                              'Rho, Vs, Vp std. dev., Rho std. dev.,'+
                              'Vs std. dev.'),
                        required=True)
                        
    parser.add_argument( 'iterations', type=int, default=1000, 
                         help='number of monte carlo simulations' )
    
    parser.add_argument('plot_type', type=str,
                        help='AVO, AB, or dashboard ',
                        default='AVO'
                        )
                        
    parser.add_argument('reflectivity_method',
                        type=reflectivity_type_hack,
                        help='Algorithm for calculating reflectivity',
                        default='zoeppritz',
                        choices=FUNCTIONS.keys()
                        ) 
                                

 
    return parser

def make_normal_dist( rock, sample_size, correlation=.8 ):
    """
    Makes a distribution of vs, vp, and rho corresponding to the
    rock properties and correlation of their uncertainties

    :param rock: A rock properties structure.
    :param sample_size: The number of samples in the distribution.
    :param correlation: The amount of correlation between the
                        uncertainties in each property.

    :returns distributions for vp, vs, rho
    """

    cor = correlation

    # Make three normalized gaussian distributions
    r = np.matrix( np.random.randn(3,sample_size ) )

    # Define a covariance matrix
    co_var = np.linalg.cholesky( np.matrix( [ [1.0,cor,cor],
                                              [cor,1.0,cor],
                                              [cor,cor,1.0]]))

    # Apply it to the distributions to add dependence
    data = co_var * r
    d1 = ( np.array(data[0,:].flat) ) *rock.vp_sig  + rock.vp
    d2 = ( np.array(data[1,:].flat)) * rock.vs_sig + rock.vs
    d3 = ( np.array( data[2,:].flat) ) * rock.rho_sig + rock.rho

    return( d1,d2,d3 )
    
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

    vp0, vs0, rho0 = make_normal_dist( Rprop0, args.iterations )
    vp1, vs1, rho1 = make_normal_dist( Rprop1, args.iterations )
    
    for i in range( args.iterations - 1 ):
        
        reflect = args.reflectivity_method( vp0[i], vs0[i], rho0[i],
                                            vp1[i], vs1[i], rho1[i],
                                            theta )
        if args.plot_type == 'AVO':        
            plt.plot( theta, reflect ,color = 'red', alpha = 0.02)
            if vp1[i] > vp0[i]:
                theta_crit = arcsin( vp0[i] / vp1[i] )*180/np.pi
                plt.axvline( x= theta_crit , color='black',alpha=0.02)
            plt.ylim((-1,1))
            data += np.nan_to_num( reflect )        
                   
        else:
            plt.scatter( reflect[0], (reflect[60]-reflect[0] ) ,
                         color = 'red' , s=20, alpha=0.05 )
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
        plt.scatter( data[0], data[60]-data[0] , color='green',
                     s=40, alpha = 0.5 ) 
        
        plt.title(args.title % locals())
        plt.ylabel('gradient [B]')
        plt.ylim(-1,1)
        plt.xlabel('intercept [A]')
        plt.xlim(-1,1)
        plt.grid()
    
    
    return get_figure_data()
    
    
def main():
    parser = ArgumentParser(usage=short_description,
                            description=__doc__)
    parser.add_argument('time', default=150, type=int, 
                        help='The size in milliseconds of the plot')
    args = parser.parse_args()
    run_script(args)
    
if __name__ == '__main__':
    main()
