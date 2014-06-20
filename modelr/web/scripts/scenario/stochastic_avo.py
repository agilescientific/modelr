from argparse import ArgumentParser
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.collections as collections
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
    co_var = np.linalg.cholesky(np.matrix([[1.0,cor,cor],
                                           [cor,1.0,cor],
                                           [cor,cor,1.0]]))

    # Apply it to the distributions to add dependence
    data = co_var * r
    d1 = (np.array(data[0,:].flat)) * rock.vp_sig  + rock.vp
    d2 = (np.array(data[1,:].flat)) * rock.vs_sig + rock.vs
    d3 = (np.array( data[2,:].flat)) * rock.rho_sig + rock.rho

    return (d1,d2,d3)
    
def run_script(args): 
    
    matplotlib.interactive(False)

    args.plot_type = 'dashboard'
    Rprop0 = args.Rock0

    Rprop1 = args.Rock1


    theta = np.arange(0,90)
    
    vp0, vs0, rho0 = make_normal_dist( Rprop0, args.iterations )
    vp1, vs1, rho1 = make_normal_dist( Rprop1, args.iterations )
    reflect = []
                      
    hist_titles = [[r'$V_\mathrm{P}$' ,  r'$m/s$'],
                    [r'$V_\mathrm{S}$' ,  r'$m/s$'],
                    [r'$\rho$' ,  r'$kg / m^3$']]
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
        
        reflect.append(args.reflectivity_method(vp0[i], vs0[i],
                                                rho0[i], vp1[i],
                                                vs1[i], rho1[i],
                                                theta))
    reflect = np.array(reflect)
    reflect = np.nan_to_num(reflect)
    #temp = np.concatenate( (vp0, rho0, vs0, vp1, rho1, vs1,), axis=0)
    
    temp = np.concatenate((vp0, vs0, rho0, vp1, vs1, rho1), axis=0)
    
    prop_samples = np.reshape(temp, (6, args.iterations))
    ave_reflect = np.mean(reflect,axis=0)
    nbins = 15
    # DO PLOTTING
        
    plt.figure(figsize = (5,13))
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
        
        # find the max bar height of the histogram for scaling the plots
        hist_max = max(hist_max,max(np.histogram(prop_samples[k],
                                                 density=True)[0]))
    
    for j in np.arange(2):
        
        upper_color = 'blue'   #color of upper histogram
        lower_color = 'green'  #color of lower histogram 
        
        for i in np.arange(3):
                
            plt.subplot(G[3+i+shift,0])
            
            plt.hist( prop_samples[i], nbins, 
                     facecolor = upper_color,
                     histtype='stepfilled', 
                     alpha = 0.25
                     ,normed = True
                     )
            plt.hist( prop_samples[i+(3)], nbins, 
                     facecolor = lower_color, 
                     histtype='stepfilled',
                     alpha = 0.25
                     ,normed = True
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
                    
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(6)
                label.set_alpha(0.5)
                
            for tick in ax.xaxis.get_major_ticks():
                tick.tick1On = True
                tick.tick2On = False
            
            # upper text label
            
            mean_props = [  [ Rprop0.vp, Rprop1.vp ],
                            [ Rprop0.vs, Rprop1.vs ],
                            [ Rprop0.rho, Rprop1.rho ] 
                            ]
                            
            which_label = ['upper','lower']  

            # Main label
            ax.text( x = limits[0,i,1], y = hist_max * 0.5, s = hist_titles[i][0], 
                    color='black', fontsize=14, alpha=0.75, 
                    horizontalalignment = 'left', verticalalignment = 'center' )   
            # Label for units
            ax.text( x = limits[0,i,1], y = hist_max * 0.25, s = hist_titles[i][1], 
                    color='black', fontsize=10, alpha=0.75, 
                    horizontalalignment = 'left', verticalalignment = 'center' )  
            
                    
            ax.text( x = float(mean_props[i][0]), y = hist_max / 5.0, s = which_label[0],
                         alpha=0.75, color=upper_color,
                         fontsize = '9',
                         horizontalalignment = 'center',
                         verticalalignment = 'center',
                         )
                         
            #lower text label             
            ax.text( x = float(mean_props[i][1]), y = hist_max / 5.0, s = which_label[1],
                         alpha=0.75, color=lower_color,
                         fontsize = '9',
                         horizontalalignment = 'center',
                         verticalalignment = 'center'
                         )
    #            
    # ax_1 the AVO plot
    #
    plt.subplot(G[0:3,:])
    plt.hold(True)
    for i in range( args.iterations -1):
        # Do the AVO template as an underlay
        # HERE        
        
        # Do the plots --> This step might not need to be in a loop
        plt.plot( theta, reflect[i] ,color = 'grey', lw = 1.0, alpha = np.min((30./args.iterations, 0.08)))
        if vp1[i] > vp0[i]:
            theta_crit = arcsin( vp0[i] / vp1[i] )*180/np.pi
            plt.axvline( x= theta_crit , color='black', lw = 1.0, alpha = np.min((30./args.iterations, 0.5)))
            
    plt.plot( theta, ave_reflect, color='black', alpha = 0.5, lw= 1.5 )
    plt.grid()
    
    # Annotation and making it look nice
    ax = plt.gca()  
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_position(('data',0))
    ax.spines['bottom'].set_alpha(0.5)
    ax.yaxis.set_ticks_position('left')
    ax.spines['left'].set_position(('data',0))
    ax.spines['left'].set_alpha(0.5)
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(6)
        label.set_alpha(0.5)

    plt.grid()
    plt.ylim((-.5,.5))
    ax.text(0.95, 0.45, 'angle',
                    verticalalignment='top', horizontalalignment='right',
                    transform=ax.transAxes,
                    color='black', fontsize=8, alpha=0.5)
    ax.text(0.05, 0.95, 'amplitude',
                    verticalalignment='top', horizontalalignment='right',
                    transform=ax.transAxes, rotation=90,
                    color='black', fontsize=8, alpha=0.5)
   
   #
   # Patches for the Background template AVO plot STARTS here
   #  
      
    a1 = 0.10    # transparency for AVO background template patches
    rangex = 90  
    band = 0.04  # thickness of Class 2 band
    # CLASS 1
    
    Path1 = mpath.Path
    path_data1 = [
        (Path1.MOVETO, (rangex * 0, 0.04)),
        (Path1.CURVE4, (rangex *0.4, 0.05)),
        (Path1.CURVE4, (rangex *0.6, -0.015)),
        (Path1.CURVE4, (rangex *1.0, -band)),
        (Path1.LINETO, (rangex *1.0, 1.0)),
        (Path1.LINETO, (rangex *0.0, 1.0)),
        (Path1.CLOSEPOLY, (rangex *0.0, 1.0)),
        ]
    codes1, verts1 = zip(*path_data1)
    path1 = mpath.Path(verts1, codes1)
    patch1 = mpatches.PathPatch(path1, facecolor='r', alpha=a1, ec = 'none')
    ax.add_patch(patch1)
    
    # plot control points and connecting lines
    x1, y1 = zip(*path1.vertices)
    #line1, = ax.plot(x1, y1, 'go-')
    
    # CLASS 2p
    
    Path2P = mpath.Path
    path_data2P = [
        (Path2P.MOVETO, (rangex * 0, band)),
        (Path2P.CURVE4, (rangex * 0.4, 0.05)),
        (Path2P.CURVE4, (rangex * 0.6, -0.015)),
        (Path2P.CURVE4, (rangex * 1.0, - band)),
        (Path2P.LINETO, (rangex * 1.0, - (band + band) )),
        (Path2P.CURVE4, (rangex * 0.6, -(0.015 + band))),
        (Path2P.CURVE4, (rangex * 0.4, 0.05 - band)),
        (Path2P.CURVE4, (rangex * 0.0, 0.0)),
        (Path2P.CLOSEPOLY, (rangex * 0.0, 0.0)),
        ]
    codes2P, verts2P = zip(*path_data2P)
    path2P = mpath.Path(verts2P, codes2P)
    patch2P = mpatches.PathPatch(path2P, facecolor='yellow', alpha=a1, ec = 'none')
    ax.add_patch(patch2P)
    
    # plot control points and connecting lines
    x2, y2 = zip(*path2P.vertices)
    #line2, = ax.plot(x2, y2, 'ro-')
    
    # CLASS 2
    
    Path2 = mpath.Path
    path_data2 = [
        (Path2.MOVETO, (rangex * 0.0, 0.0)),
        (Path2.CURVE4, (rangex * 0.4, 0.05 - band)),
        (Path2.CURVE4, (rangex * 0.6, -(0.015 + band))),
        (Path2.CURVE4, (rangex * 1.0, - (band + band))),
        (Path2.LINETO, (rangex * 1.0,  - (3 * band))),
        (Path2.CURVE4, (rangex * 0.6, - (0.015 + 2*band))),
        (Path2.CURVE4, (rangex * 0.4, 0.05 - (0.0 + 2*band))),
        (Path2.CURVE4, (rangex * 0.0, - band)),
        (Path2.CLOSEPOLY, (rangex * 0.0, 0.0)),
        ]
    codes2, verts2 = zip(*path_data2)
    path2 = mpath.Path(verts2, codes2)
    patch2 = mpatches.PathPatch(path2, facecolor='green', alpha=a1, ec = 'none')
    ax.add_patch(patch2)
    
    # plot control points and connecting lines
    x2, y2 = zip(*path2.vertices)
    
    #line2, = ax.plot(x2, y2, 'ro-')
    
    # CLASS 3
    Path3 = mpath.Path
    path_data3 = [
        (Path3.MOVETO, (rangex * 0.0, - band)),
        (Path3.CURVE4, (rangex * 0.4, 0.05 - (0.0 + 2*band))),
        (Path3.CURVE4, (rangex * 0.6, - (0.015 + 2*band))),
        (Path3.CURVE4, (rangex * 1.0, - (3 * band))),
        (Path3.LINETO, (rangex * 1.0, -1.0)),
        (Path3.LINETO, (rangex * 0.0, -1.0)),
        (Path3.CLOSEPOLY, (rangex * 0.0, -1.0)),
        ]
    codes3, verts3 = zip(*path_data3)
    path3 = mpath.Path(verts3, codes3)
    patch3 = mpatches.PathPatch(path3, facecolor='blue', alpha=a1, ec = 'none')
    ax.add_patch(patch3)
    
    # plot control points and connecting lines
    x3, y3 = zip(*path3.vertices)
    #line2, = ax.plot(x2, y2, 'ro-')
    
    ax.grid()
    
    ax.text(0.98, 0.98, 'Amplitude vs angle',
                verticalalignment='top',
                horizontalalignment='right',
                transform=ax.transAxes,
                color='black', fontsize=9, fontweight = 'bold', alpha=0.5)
                
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_position(('data',0))
    ax.yaxis.set_ticks_position('left')
    ax.spines['left'].set_position(('data',0))
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(8)
        label.set_alpha(0.5)
    
    plt.grid() 
    
    # Class 1 label  
    
    # y-values for class labels 1,2p, 2, 3, and 4 respectively
    ylabelcntrs = [ 0.35, 0.025, -0.025, -0.4, -0.2  ]
    xctrs = 10
    
    fs = 10 # fontsize 
    
    a2 = 0.4   # transparency value for Gradient vs Intercept text 
                
    ax.text( xctrs, ylabelcntrs[0], 'CLASS 1',
                verticalalignment='center',
                horizontalalignment='left',
                color='red', fontsize=fs, fontweight = 'bold', alpha=a2)
                
    # Class 2p label     
    ax.text( xctrs, ylabelcntrs[1], 'CLASS 2p',
                verticalalignment='center',
                horizontalalignment='left',
                rotation = -3,
                color='#EEC900', fontsize=fs, fontweight = 'bold', alpha=a2 * 1.5)
                
    # Class 2 label     
    ax.text( xctrs, ylabelcntrs[2], 'CLASS 2',
                verticalalignment='center',
                horizontalalignment='left',
                rotation = -3,
                color='green', fontsize=fs, fontweight = 'bold', alpha=a2)
                
    # Class 3 label     
    ax.text( xctrs, ylabelcntrs[3],  'CLASS 3',
                verticalalignment='center',
                horizontalalignment='left',
                rotation = -15,
                color='blue', fontsize=fs, fontweight = 'bold', alpha=a2)   
                
    # Class 4 label     
    ax.text( xctrs, ylabelcntrs[4],  'CLASS 4',
                verticalalignment='center',
                horizontalalignment='left',
                rotation = 15,
                color='#B048B5', fontsize=fs, fontweight = 'bold', alpha=a2)  
    #
    # Patches for background template AVO plot ENDS here
    #
    

                            
    # ax_2 the AB plot
    plt.subplot(G[0+shift:3+shift,:])
    plt.hold(True)
    for i in range( args.iterations -1):

        plt.scatter( reflect[i,0], (reflect[i,50]-reflect[i,0] ),
                     color = 'grey' , s = 20,
                     alpha = np.max((30./args.iterations, 0.2)) )
                     
    # Plot the average of the dots
    plt.scatter( ave_reflect[0], ave_reflect[50]- ave_reflect[0],
                 color = 'black' , s = 40, alpha= 0.5 )  
    
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
    
    plt.grid()
    
    # axis limits
    
    ylimits = (np.amin((-.3,np.nanmin(reflect[:,50]-reflect[:,0]))),
              np.amax((.3,np.nanmax(reflect[:,50]-reflect[:,0]))))
    xlimits = (np.amin((-.3,np.nanmin(reflect[:,0]))),
              np.amax((.3,np.nanmax(reflect[:,0]))))
    
    plt.ylim( ylimits )
    
    plt.xlim( xlimits )
    
    # axis labels
    
    ax.text(xlimits[1]-0.05, 0.025, 'intercept',
                    verticalalignment='center',
                    horizontalalignment='right',
                    #transform=ax.transAxes,
                    color='black', fontsize=8, alpha=0.5)
    
    ax.text( 0.025, ylimits[1]-0.05, 'gradient', rotation=90,
            verticalalignment='top', horizontalalignment='center',
            #transform=ax.transAxes,
            color='black', fontsize=8, alpha=0.5)
    #
    # Patches for background Gradient vs Intercept template STARTS here
    #
     
    x = np.arange(xlimits[0], xlimits[1], 0.01)
    y = np.arange(ylimits[0], ylimits[1], 0.01)
    
    s0 = -x
    
    shift2 = 0.04 #width for class2 width in plot
    
    height_ellipse = 0.05
    width_ellipse = 3.0
    
    # Plot background trend (diagonal line)
    ax.plot(x, s0, color='black', alpha = a1)
    
    # add a rectangle for class 2 neg
    lowleft2 = (-shift2,-1.0)
    
    class2neg = mpatches.Rectangle( lowleft2, width = abs(lowleft2[0]), height = 1.0,
                                color = 'green',
                                alpha = a1,
                                ec = "white",
                                lw = 4)
    ax.add_patch(class2neg)
    
    # add a rectange for class 2 pos
    lowleft2pos = (0.0, 0.0)
    class2pos = mpatches.Rectangle( lowleft2pos, width = abs(lowleft2[0]), height = 1.0,
                                color = 'green',
                                alpha = a1,
                                ec="white",
                                lw = 4)   
    ax.add_patch(class2pos)
                
    # add a rectange for class 2p pos
    lowleft2Ppos = (-shift2, 0.0)
    class2Ppos = mpatches.Rectangle( lowleft2Ppos, width = abs(lowleft2[0]), height = 1.0,
                                color = 'yellow',
                                alpha = a1,
                                ec="white",
                                lw = 4)   
    ax.add_patch(class2Ppos)
                            
    # add a rectange for class 2p neg
    lowleft2Pneg = (0.0, -1.0)
    class2Ppos = mpatches.Rectangle( lowleft2Pneg, width = abs(lowleft2[0]), height = 1.0,
                                color = 'yellow',
                                alpha = a1,
                                ec="white",
                                lw = 4)   
    ax.add_patch(class2Ppos)
    
    # add rectangle for lower left quadrant class 3
    lowleft3neg = (-1.0, -1.0)
    class3neg = mpatches.Rectangle(lowleft3neg, width = 1.0 + lowleft2[0], height = 1.0, 
                                    color = 'blue',
                                    alpha = a1,
                                    ec = 'none')
    ax.add_patch(class3neg)
    
    # add rectange for upper right quadrant class 3
    lowleft3pos = (shift2, 0)
    class3pos = mpatches.Rectangle(lowleft3pos, width = 1.0 + lowleft2[0], height = 1.0,
                                    color = 'blue',
                                    alpha = a1,
                                    ec = 'none')
    ax.add_patch(class3pos)
    
    # add a Polygon for Class 4 upper left quadrant
    # add a path patch
    Path4u = mpath.Path
    path_data4u = [
        (Path4u.MOVETO, [ -1.0, 0.0 ]),
        (Path4u.LINETO, [-1.0,  1.0]),
        (Path4u.LINETO, [ -shift2,  shift2]),
        (Path4u.LINETO, [ -shift2, 0]),
        (Path4u.CLOSEPOLY, [-shift2, 0.0])
        ]
    codes4u, verts4u = zip(*path_data4u)
    path4u = mpath.Path(verts4u, codes4u)
    patch4u = mpatches.PathPatch(path4u, facecolor = '#B048B5',    # purple
                        alpha = a1,
                        ec = 'none')
    ax.add_patch(patch4u)
    
    # add a Polygon for Class 4 lower right quadrant
    
    Path4l = mpath.Path
    path_data4l = [
        (Path4l.MOVETO, [ shift2, 0.0 ]),
        (Path4l.LINETO, [ 1.0,  0.0]),
        (Path4l.LINETO, [ 1.0,  -1.0]),
        (Path4l.LINETO, [ shift2, -shift2 ]),
        (Path4l.CLOSEPOLY, [shift2, -shift2])
        ]
    codes4l, verts4l = zip(*path_data4l)
    path4l = mpath.Path(verts4l, codes4l)
    patch4l = mpatches.PathPatch(path4l, facecolor = '#B048B5',    # purple
                        alpha = a1,
                        ec = 'none')
    ax.add_patch(patch4l)
    
    
    # Add a Polygon for the Class 1 upper right quadrant
    
    Path1u = mpath.Path
    path_data1u = [
        (Path1u.MOVETO, [ -shift2, shift2 ]),
        (Path1u.LINETO, [ -1.0,  1.0]),
        (Path1u.LINETO, [ -shift2,  1.0]),
        (Path1u.CLOSEPOLY, [-shift2, shift2])
        ]
    codes1u, verts1u = zip(*path_data1u)
    path1u = mpath.Path(verts1u, codes1u)
    patch1u = mpatches.PathPatch(path1u, facecolor = 'red',
                        alpha = a1,
                        ec = 'none')
    ax.add_patch(patch1u)
    
    # Add a Polygone for the Class 1 lower left quadrant
    Path1l = mpath.Path
    path_data1l = [
        (Path1l.MOVETO, [ shift2, -shift2 ]),
        (Path1l.LINETO, [ shift2,  -1.0]),
        (Path1l.LINETO, [ 1.0,  -1.0]),
        (Path1l.CLOSEPOLY, [shift2, -shift2])
        ]
    codes1l, verts1l = zip(*path_data1l)
    path1l = mpath.Path(verts1l, codes1l)
    patch1l = mpatches.PathPatch(path1l, facecolor = 'red',
                        alpha = a1,
                        ec = 'none')
    ax.add_patch(patch1l)
    
    # Draw ellipse
    xy = np.hstack((0,0))
    
    bkgd = collections.EllipseCollection(
                            widths = width_ellipse, 
                            heights = height_ellipse, 
                            angles = 135, units = 'xy', 
                            offsets = xy,
                            transOffset = ax.transData,
                            facecolor = 'grey',
                            edgecolor = 'none',
                            alpha = 0.15
                            )
    
    ax.add_collection(bkgd)
    
    #Get rid of axes spines
    
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_position(('data',0))
    ax.spines['bottom'].set_alpha(0.5)
    ax.yaxis.set_ticks_position('left')
    ax.spines['left'].set_position(('data',0))
    ax.spines['left'].set_alpha(0.5)
    
    # Annotation for Gradient vs Intercept annotation
    
    ax.text(0.98, 0.98, 'Gradient vs intercept',
            verticalalignment='top',
            horizontalalignment='right',
            transform=ax.transAxes,
            color='black', fontsize=9, fontweight = 'bold', alpha=0.50)
    
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(8)
        label.set_alpha(0.5)
            
    # Class 1 label  
       
    ax.text(3 * shift2, ylimits[0]+shift2, 'CLASS 1',
                verticalalignment='center',
                horizontalalignment='center',
                color='red', fontsize=fs, fontweight = 'bold', alpha=a2)
                
    # Class 2 label     
    ax.text( -0.5 * shift2, ylimits[0] + 0.5 * shift2, 'CLASS 2',
                verticalalignment='bottom',
                horizontalalignment='center',
                rotation = 90,
                color='green', fontsize=fs, fontweight = 'bold', alpha=a2)
                
    # Class 2P label     
    ax.text( 0.5 * shift2, ylimits[0] + 0.5 * shift2, 'CLASS 2p',
                verticalalignment='bottom',
                horizontalalignment='center',
                rotation = 90,
                color='#EEC900', fontsize=fs, fontweight = 'bold', alpha=a2 * 1.5)
                
    # Class 3 label     
    ax.text(- 3 * shift2, ylimits[0]+shift2,  'CLASS 3',
                verticalalignment='center',
                horizontalalignment='right',
                color='blue', fontsize=fs, fontweight = 'bold', alpha=a2)
        
    # Class 4 label     
    ax.text(-3 * shift2, shift2, 'CLASS 4',
                verticalalignment='center',
                horizontalalignment='right',
                color='#B048B5', fontsize=fs, fontweight = 'bold', alpha=a2)
                
    # Background label  
    angle = -45
          
    ax.text( 0.1 * height_ellipse, 0.1 * height_ellipse, 'background',
                verticalalignment='center',
                horizontalalignment='center',
                rotation = angle,
                transform=ax.transData,
                color='black', fontsize=fs, fontweight = 'bold', alpha=a2/2.0)
                              
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
