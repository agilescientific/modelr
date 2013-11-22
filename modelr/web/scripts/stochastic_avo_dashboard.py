from argparse import ArgumentParser
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from modelr.web.urlargparse import rock_properties_type,\
     reflectivity_type
from modelr.rock_properties import MODELS
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
                        choices=MODELS.keys())
                        
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
        fig =plt.figure(figsize = (15,4))
        fig.subplots_adjust(bottom=0.025, left=0.025, top = 0.975, right=0.975)
        fig.hold(True)
        G = gridspec.GridSpec(2,9)
    
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
            #data += np.nan_to_num( reflect )        
                   
        if args.plot_type == 'AB':
            plt.scatter( reflect[0], (reflect[60]-reflect[0] ) , color = 'red' , s=20, alpha=0.05 )
            #data += np.nan_to_num( reflect )   
            
        #do dashboard plot:
        if args.plot_type == 'dashboard':
                    
            #ax_1
            ax_1 = plt.subplot(G[:,0:3])
            plt.hold(True)        
            plt.plot( theta, reflect ,color = 'red', alpha = 0.1)
            #plt.grid()
    
            if vp1 > vp0:
                theta_crit = arcsin( vp0 / vp1 )*180/np.pi
                plt.axvline( x= theta_crit , color='black',alpha=.5 )
            plt.ylim((-1,1))
            #data += np.nan_to_num( reflect )
                            
            plt.xticks([]), plt.yticks([])
            #plt.text(0.14,0.5, 'AVO plot',ha='center',va='center',size=10,alpha=.5)
                    
            #ax_2
            ax_2 = plt.subplot(G[:,3:6])
            plt.hold(True)
            plt.scatter( reflect[0], (reflect[60]-reflect[0] ) , color = 'red' , s=20, alpha=0.02 )
            #data += np.nan_to_num( reflect )   
            plt.xticks([]), plt.yticks([])
            #plt.grid()
            #plt.text(0.50,0.5, 'Int-Gradient plot',ha='center',va='center',size=10,alpha=.5)
                        
    #data /= args.iterations
    '''
    if args.plot_type == 'AVO':
        
        plt.plot( theta, data, color='green' )
        
        plt.title(args.title % locals())
        plt.ylabel('reflectivity')
        plt.ylim(-1,1)
        plt.xlabel('offset (degrees)')
        plt.grid()
    
    if args.plot_type == 'AB':
        plt.scatter( data[0], data[60]-data[0] , color='green', s=40, alpha = 0.5 ) 
        plt.title(args.title % locals())
        plt.ylabel('gradient [B]')
        plt.ylim(-1,1)
        plt.xlabel('intercept [A]')
        plt.xlim(-1,1)
        plt.grid()       
    '''
    if args.plot_type == 'dashboard':
        #ax_3
        ax_3 = plt.subplot(G[0,6])
        plt.hist(np.random.normal(Rprop0.vp, Rprop0.vp_sig, args.iterations), 50)
        plt.xticks([]), plt.yticks([])
        #plt.text(0.70,0.66, 'vp0',ha='center',va='center',size=10,alpha=.5)
            
        #ax_4
        ax_4 = plt.subplot(G[0,7])
        plt.hist(np.random.normal(Rprop0.vs, Rprop0.vs_sig, args.iterations), 50)
        plt.xticks([]), plt.yticks([])
        #plt.text(0.85,0.66, 'vs0',ha='center',va='center',size=10,alpha=.5)
        
        #ax_5
        ax_5 = plt.subplot(G[0,8])
        plt.hist(np.random.normal(Rprop0.rho, Rprop0.rho_sig, args.iterations), 50)
        plt.xticks([]), plt.yticks([])
        #plt.text(0.92,0.66, 'rho0',ha='center',va='center',size=10,alpha=.5)
        
        #ax_6
        ax_6 = plt.subplot(G[1,6])
        plt.hist(np.random.normal(Rprop1.vp, Rprop1.vp_sig, args.iterations), 50)
        plt.xticks([]), plt.yticks([])
        #plt.text(0.70,0.33, 'vp0',ha='center',va='center',size=10,alpha=.5)
        
        #ax_7
        ax_7 = plt.subplot(G[1,7])
        plt.hist(np.random.normal(Rprop1.vs, Rprop1.vs_sig, args.iterations),50)
        plt.xticks([]), plt.yticks([])
        #plt.text(0.85,0.33, 'vs0',ha='center',va='center',size=10,alpha=.5)
        
        #ax_8
        ax_8 = plt.subplot(G[1,8])
        plt.hist(np.random.normal(Rprop1.rho, Rprop1.rho_sig, args.iterations),50)
        plt.xticks([]), plt.yticks([])
        plt.text(0.92,0.33, 'rho0',ha='center',va='center',size=10,alpha=.5)
        plt.axis('tight')
        #savefig('../figures/multiplot_ex.png',dpi=48)
        plt.show()

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
