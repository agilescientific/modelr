from argparse import ArgumentParser
import matplotlib
import matplotlib.pyplot as plt
from modelr.web.urlargparse import rock_properties_type,\
      reflectivity_type
from modelr.web.defaults import default_parsers
from modelr.constants import REFLECTION_MODELS as MODELS

from modelr.web.util import get_figure_data
import numpy as np
from scipy import arcsin
import multiprocessing as mp

short_description = (
    "Make a stochastic avo plot using monte carlo " +
    "simulation around the rock property uncertainties."
    )

def add_arguments(parser):


                            

    parser.add_argument('Rock0', type=rock_properties_type, 
                        help=('Upper rock type'),
                        default = '2900, 1600, 2600, 29, 16, 26',
                        required=True)
    
    parser.add_argument('Rock1', type=rock_properties_type, 
                        help=('Lower rock type'),
                        default = '3200, 1900, 2500, 32, 19, 25',
                        required=True)
                        
    parser.add_argument( 'iterations', type=int, default=50, 
                         help='number of monte carlo simulations' )
    
                        
    parser.add_argument('reflectivity_method',
                        type=reflectivity_type,
                        help='Algorithm for calculating reflectivity',
                        default='zoeppritz',
                        choices=MODELS.keys(),
                        ) 
                                

 
    return parser

def make_normal_dist( rock, sample_size, correlation=.8 ):
    """
    Makes a distribution of vs, vp, and rho corresponding to the
    rock properties and correlation of their uncertainties

    :param rock: A rock properties structure.
    :param sample_size: The number of samples in the distribution.
    :keyword correlation: The amount of correlation between the
                        uncertainties in each property.

    :returns: distributions for vp, vs, rho
    """

    #pid = mp.current_process()._identity[0]
    #np.random.seed(pid)
    
    cor = correlation

    # Make three normalized gaussian distributions
    r = np.matrix( np.random.randn(3,sample_size ) )

    # Define a covariance matrix
    co_var = np.linalg.cholesky( np.matrix( [ [1.0,cor,cor],
                                              [cor,1.0,cor],
                                              [cor,cor,1.0]]))

    # Apply it to the distributions to add dependence
    data = co_var * r
    d1 = ( np.array(data[0,:].flat) ) * rock.vp_sig  + rock.vp
    d2 = ( np.array(data[1,:].flat)) * rock.vs_sig + rock.vs
    d3 = ( np.array( data[2,:].flat) ) * rock.rho_sig + rock.rho

    return( d1,d2,d3 )
    
def run_script(args): 
    
    matplotlib.interactive(False)

    args.plot_type = 'dashboard'
    Rprop0 = args.Rock0
    Rprop1 = args.Rock1

    theta = np.arange(0,90)
    
    vp0, vs0, rho0 = make_normal_dist( Rprop0, args.iterations )
    vp1, vs1, rho1 = make_normal_dist( Rprop1, args.iterations )
    reflect = []
    names = np.array([['Vp0','Vs0','rho0'],['Vp1','Vs1','rho1']])
    nbins = 15

    vp_lim = ( np.amin((Rprop1.vp - ( 3.* Rprop1.vp_sig ),
                        Rprop0.vp - ( 3.* Rprop1.vp_sig ) ) ),
                        np.amax((Rprop1.vp + ( 3.* Rprop1.vp_sig ),
                        Rprop0.vp + ( 3.* Rprop1.vp_sig ) ) ) )

    vs_lim = ( np.amin((Rprop1.vs - ( 3.* Rprop1.vs_sig ),
                        Rprop0.vs - ( 3.* Rprop1.vs_sig ) ) ),
                        np.amax((Rprop1.vs + ( 3.* Rprop1.vs_sig ),
                        Rprop0.vs + ( 3.* Rprop1.vs_sig ) ) ) )
                        
    rho_lim = ( np.amin((Rprop1.rho - ( 3.* Rprop1.rho_sig ),
                        Rprop0.rho - ( 3.* Rprop1.rho_sig ) ) ),
                        np.amax((Rprop1.rho + ( 3.* Rprop1.rho_sig ),
                        Rprop0.rho + ( 3.* Rprop1.rho_sig ) ) ) )
    
    limits = np.array([[ vp_lim, vs_lim, rho_lim ],
                       [ vp_lim, vs_lim, rho_lim ] ])
    
    for i in range( args.iterations ):
        
        reflect.append( args.reflectivity_method( vp0[i], vs0[i], rho0[i],
                                                  vp1[i], vs1[i], rho1[i],
                                                  theta) )
    reflect = np.array(reflect)
    temp = np.concatenate( (vp0, vs0, rho0, vp1, vs1, rho1), axis=0)
    prop_samples = np.reshape(temp, (6, args.iterations))
    ave_reflect = np.mean(reflect,axis=0)
    nbins = 15
    # DO PLOTTING
        
    plt.figure(figsize = (4,10))
    plt.subplots_adjust(bottom=0.1, left=0.1, top = 1, right=0.9)
    plt.hold(True)
    if args.plot_type == 'dashboard':
        G = matplotlib.gridspec.GridSpec(9,2, hspace=0.5)
        shift=3
    else:
        G = matplotlib.gridspec.GridSpec(2,6)
        shift=0
    
    # histogram plots (ax_3, ax_4, ax_5, ax_6, ax_7, ax_8)
    hist_max = 0
    for k in np.arange(len(prop_samples)):
        hist_max = max(hist_max,max(np.histogram(prop_samples[k],
                                                 density=True)[0]))
    
    for j in np.arange(2):
        for i in np.arange(3):
            plt.subplot(G[3+i+shift,j])
            plt.hist( prop_samples[i+(3*j)], nbins, 
                     facecolor='gray', 
                     alpha=0.25,
                     normed = True
                     )
            temp = plt.gca()
            
            # Annotation and making it look nice
            plt.axis([limits[j][i][0], limits[j][i][1],
                      temp.axis()[2], hist_max ])
            plt.yticks([])
            plt.xticks( rotation=90,horizontalalignment='left' )
            ax = plt.gca()  
            ax.spines['right'].set_color('none')
            ax.spines['left'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.spines['bottom'].set_alpha(0.5)
            ax.text(0.5, 0.8, names[j,i],
                    verticalalignment='bottom', horizontalalignment='center',
                    transform=ax.transAxes, 
                    color='black', fontsize=8, alpha=0.75)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(6)
                label.set_alpha(0.5)
                label.set_bbox(dict(facecolor='white',
                                    edgecolor='None', alpha=0.35))
                
            for tick in ax.xaxis.get_major_ticks():
                tick.tick1On = True
                tick.tick2On = False      
    
    # ax_1 the AVO plot
    plt.subplot(G[0:3,:])
    plt.hold(True)
    for i in range( args.iterations -1):
        # Do the AVO template as an underlay
        # HERE        
        
        # Do the plots --> This step might not need to be in a loop
        plt.plot( theta, reflect[i] ,color = 'red', alpha = np.min((10./args.iterations, 0.5)))
        if vp1[i] > vp0[i]:
            theta_crit = arcsin( vp0[i] / vp1[i] )*180/np.pi
            plt.axvline( x= theta_crit , color='black', alpha = np.min((10./args.iterations,0.5)))
    plt.plot( theta, ave_reflect, color='green', alpha = 0.5 )
    plt.grid()
    
    # Annotation and making it look nice
    ax = plt.gca()  
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_position(('data',0))
    ax.yaxis.set_ticks_position('left')
    ax.spines['left'].set_position(('data',0))
    ax.text(0.5, 0.95, 'AVO plot',
                    verticalalignment='top', horizontalalignment='center',
                    transform=ax.transAxes,
                    color='black', fontsize=10, alpha=0.75)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(7)
        label.set_alpha(0.5)
        label.set_bbox(dict(facecolor='white', edgecolor='None', alpha=0.35))
    plt.grid()
    plt.ylim((-.5,.5))
    ax.text(0.95, 0.45, 'angle',
                    verticalalignment='top', horizontalalignment='right',
                    transform=ax.transAxes,
                    color='black', fontsize=8, alpha=0.75)
    ax.text(0.05, 0.95, 'amplitude',
                    verticalalignment='top', horizontalalignment='right',
                    transform=ax.transAxes, rotation=90,
                    color='black', fontsize=8, alpha=0.75)
   
                       
    # ax_2 the AB plot
    plt.subplot(G[0+shift:3+shift,:])
    plt.hold(True)
    for i in range( args.iterations -1):
        # Do the underlay for the intercept-gradient template
        # load image...or make rectangles:
        
        # Class 1
        
        # Class 2
        
        # Class 2p
        
        # Class 3
        
        # Class 4
        
        # Plot the dots
        plt.scatter( reflect[i,0], (reflect[i,50]-reflect[i,0] ),
                     color = 'red' , s=20,
                     alpha = np.min((10./args.iterations,0.5)) )
                     
    # Plot the average of the dots
    plt.scatter( ave_reflect[0], ave_reflect[50]- ave_reflect[0],
                 color = 'green' , s=20, alpha=.5 )  
    
    # Annotation and making it nice
    plt.xticks([]), plt.yticks([])
    ax = plt.gca()    
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_position(('data',0))
    ax.spines['bottom'].set_alpha(0.5)
    ax.yaxis.set_ticks_position('left')
    ax.spines['left'].set_position(('data',0))
    ax.spines['left'].set_alpha(0.5)
    
    ax.text(0.05, 0.95, 'Intercept-Gradient\ncrossplot',
            verticalalignment='top',
            horizontalalignment='left',
            transform=ax.transAxes,
            color='black', fontsize=10, alpha=0.75)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(7)
        label.set_alpha(0.5)
        label.set_bbox(dict(facecolor='white',
                            edgecolor='None',
                            alpha=0.35))
    plt.grid()
    # axis limits
    plt.ylim((np.amin((-.3,np.nanmin(reflect[:,50]-reflect[:,0]))),
              np.amax((.3,np.nanmax(reflect[:,50]-reflect[:,0])))) )
    
    plt.xlim((np.amin((-.3,np.nanmin(reflect[:,0]))),
              np.amax((.3,np.nanmax(reflect[:,0])))))
    # axis labels
    ax.text(1.0, 0.55, 'intercept',
                    verticalalignment='top',
                    horizontalalignment='right',
                    transform=ax.transAxes,
                    color='black', fontsize=8, alpha=0.5)
    ax.text(0.55, 1.0, 'gradient', rotation=90,
            verticalalignment='top', horizontalalignment='right',
            transform=ax.transAxes,
            color='black', fontsize=8, alpha=0.5)
    #plt.text(-0.15, 0.5, 'Intercept-Gradient plot',ha='left',
    #va='center',size=10,alpha=.5)
                              
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
