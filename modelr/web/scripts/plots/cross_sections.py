
from matplotlib import cm
from matplotlib import gridspec
import h5py

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import numpy as np
from modelr.web.util import get_figure_data

short_description = ('Look at plots '
                     'across spatial, offset, and frequency '
                     'cross-sections')



def add_arguments(parser):


    parser.add_argument('theta',
                        type=float,
                        default=0,
                        help="Offset angle",
                        interface='slider',
                        range=[0,45])
    
                        
    parser.add_argument('trace',
                        type=int,
                        help='Trace',
                        default=25,
                        interface='slider',
                        range=[1,350])

    parser.add_argument('time',
                        type=float,
                        range=[0,100],
                        default=0,
                        interface='slider',
                        help='twt')

    return parser




def run_script(earth_model, seismic_model,
               args):


    cmap = 'seismic'
    #max/min amplitude for plot and colorbar scaling
    extr1 = 1.0

    # Define the figure layout
    fig = plt.figure(figsize=[15,10], facecolor = 'white')
    width_ratios = [3,1,1]
    gs = gridspec.GridSpec(2, 3, width_ratios = width_ratios,
                           height_ratios = [2,1])

    # Make the array of subplot
    ax11 = plt.subplot(gs[0])
    ax12 = plt.subplot(gs[1])
    ax13 = plt.subplot(gs[2])
    ax21 = plt.subplot(gs[3])
    ax22 = plt.subplot(gs[4])
    ax23 = plt.subplot(gs[5])

    axarr = [[ax11, ax12, ax13],[ax21, ax22, ax23]]

    # spatial
    seismic_model.go(earth_model, theta=args.theta)
    seismic_data = np.nan_to_num(seismic_model.seismic)

    
    im = axarr[0][0].imshow(seismic_data[:,:, 0, 0], 
                            aspect='auto', cmap=cmap, 
                            extent = [0, seismic_data.shape[1],
                                      seismic_data.shape[0],
                                      0],
                                      vmin = -extr1,
                                      vmax = extr1,
                            interpolation='spline16')

    locs,labels = plt.yticks()
    labels = np.linspace(0,
                         seismic_data.shape[0]*seismic_model.dt*100,
                         num=np.size(locs)+1)
    axarr[0][0].set_yticklabels(labels.astype(int).astype(str))
    
    axarr[0][0].axvline(x=args.trace-1, lw=3, color='k', alpha=0.25)
    axarr[0][0].axhline(y=args.time, lw=3,
                        color='g')
    axarr[0][0].set_title('spatial cross-section')
    axarr[0][0].set_ylabel('time [ms]')
    axarr[0][0].set_xticklabels(' ')
    axarr[0][0].grid()

    # Put wiggle trace on seismic cross-section
    trace1 = seismic_data[:,args.trace-1, 0, 0]
    x = np.arange(seismic_data.shape[0])
    gain1 = 5.0

    axarr[0][0].plot(args.trace -1  + gain1 * trace1, x, 'k', alpha = 0.9)
    axarr[0][0].fill_betweenx(x, args.trace+gain1 * trace1,
                              args.trace-1, 
                              gain1 * trace1 > 0,
                              color = 'k', alpha = 0.5)


    # Put colorbar legend
    colorbar_ax = fig.add_axes([0.55,0.775,0.010,0.08])
    fig.colorbar(im, cax=colorbar_ax)
    colorbar_ax.text( 0.5, -0.1, '%3.2f' % -extr1, transform=colorbar_ax.transAxes, horizontalalignment='center',verticalalignment='top')
    colorbar_ax.text(0.5, 1.1, '%3.2f' % extr1, transform=colorbar_ax.transAxes, horizontalalignment='center')
    colorbar_ax.set_axis_off()

    axarr[1][0].plot(seismic_data[args.time,:,
                                  0, 0], 'g', lw = 3)
    axarr[1][0].set_ylim(-extr1,extr1)
    axarr[1][0].set_xlim(0,seismic_data.shape[1])
    axarr[1][0].set_ylabel('amplitude')
    axarr[1][0].set_xlabel('trace')
    axarr[1][0].grid()

    # angle column
    seismic_model.go(earth_model,
                     traces=args.trace-1)
    seismic_data = seismic_model.seismic
    
    axarr[0][1].imshow(seismic_data[:, 0, :, 0], 
                       aspect='auto', cmap=cmap, 
                       extent=[0, seismic_data.shape[2], 
                             seismic_data.shape[0],
                                 0],
                                 vmin = -extr1, vmax = extr1,
                       interpolation='spline16'
                                 )


    
    axarr[0][1].axvline(x=args.theta, lw=3, color='r', alpha = 0.25)
    axarr[0][1].axhline(y=args.time,
                        lw=3, color='g')
    axarr[0][1].set_title('angle gather')
    axarr[0][1].set_yticklabels(' ')
    axarr[0][1].set_xticklabels(' ')
    axarr[0][1].grid()

    # Put wiggle trace on AVO cross-section
    trace2 = seismic_data[:,0, args.theta, 0]
    x = np.arange(seismic_data.shape[0])
    gain2 = gain1*float(width_ratios[0])/width_ratios[1]

    axarr[0][1].plot(args.theta + gain2 * trace2, x, 'k', alpha = 0.9)
    axarr[0][1].fill_betweenx(x, args.theta + gain2 * trace2,
                              args.theta, 
                              gain2 * trace2 > 0,
                              color = 'k', alpha = 0.5)
    # line plot
    data2 = seismic_data[args.time, 0,:, 0]
    axarr[1][1].plot(data2, 'g', lw = 3)
    axarr[1][1].set_ylim(-extr1,extr1)
    axarr[1][1].set_xlim(0,seismic_data.shape[2])
    axarr[1][1].set_xlabel(r'$\theta$'+' '+r'$^{\circ}$')
    axarr[1][1].set_yticklabels(' ')
    axarr[1][1].set_xticks([10,20,30,40])
    axarr[1][1].grid()


    
    # wavelet
    f = seismic_model.start_f
    seismic_model.start_f = 8.0
    seismic_model.end_f = 100.0
    seismic_model.go(earth_model, traces=args.trace-1,
                     theta=args.theta)
    seismic_data = seismic_model.seismic

    
    axarr[0][2].imshow(seismic_data[:, 0, 0, :],
                       aspect='auto', cmap=cmap, 
                       extent = [0, seismic_data.shape[3],
                                 seismic_data.shape[0], 0],
                       vmin = -extr1, vmax = extr1,
                       interpolation='spline16'
                       )
    axarr[0][2].axvline(x=f, lw=3, color='m', alpha = 0.25)
    axarr[0][2].axhline(y=args.time,
                        lw=3, color='g')
    axarr[0][2].set_title('wavelet gather')
    axarr[0][2].set_yticklabels(' ')
    axarr[0][2].set_xticklabels(' ')
    axarr[0][2].grid()

    # Put wiggle trace on wavelet cross-section
    
    trace3 = seismic_data[:,0, 0, f]
    x = np.arange(seismic_data.shape[0])
    gain3 = gain1*float(width_ratios[0])/float(width_ratios[2])

    axarr[0][2].plot(f + gain3 * trace3, x, 'k', alpha = 0.9)
    axarr[0][2].fill_betweenx(x, f + gain3 * trace3, f, 
                              gain3 * trace3 > 0,
                              color = 'k', alpha = 0.5)
    #line plot
    data3 = seismic_data[args.time, 0, 0, :]
    axarr[1][2].plot(seismic_model.wavelet_cf(),
                     data3, 'g', lw = 3)
    axarr[1][2].set_ylim(-extr1,extr1)
    axarr[1][2].set_xlabel('center frequency ' + r'$Hz$')
    axarr[1][2].set_xscale('log', basex=2)
    axarr[1][2].set_xlim(seismic_model.wavelet_cf()[0],
                         seismic_model.wavelet_cf()[-1])
    axarr[1][2].set_yticklabels(' ')
    axarr[1][2].grid()
    
    # remove some whitespace between the axes
    gs.update(hspace=0.05,wspace=0.05)

    seismic_model.start_f = 8
    seismic_model.end_f = 100
    return get_figure_data()