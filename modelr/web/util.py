'''
==================
modelr.web.util
==================

Created on May 3, 2012

@author: sean
'''
import gc
import tempfile
import matplotlib as mpl
import matplotlib.pyplot as plt
from agilegeo.wavelet import ricker
import numpy as np
from scipy.signal import hilbert
from modelr.reflectivity import get_reflectivity, do_convolve

        
def get_figure_data(transparent=False):
    '''
    Return the current plot as a binary blob. 
    '''
    fig_path = tempfile.SpooledTemporaryFile(suffix='.png')
    plt.savefig(fig_path, transparent=transparent)
    plt.close()

    fig_path.seek(0)
    with fig_path as fd:
        data = fd.read()

        
    # Alternative approach to do it in memory rather than on disk
    #image_file = tempfile.SpooledTemporaryFile(suffix='.png')
    #plt.savefig(image_file, format='png') 
    #data = image_file.read()
    #image_file.close()
    return data


def wiggle(data, tstart,dt=1, line_colour='black',
           fill_colour='blue',
           opacity= 0.5, skipt=0, gain=1, lwidth=.5, xax=1,
           quadrant=plt):
    """
    Make a wiggle trace and plots it on the current figure.
    
    :param data: as a 2D array indexed as [samples, traces]      
    :param dt: sample interval of the data [seconds].
    :param skipt: number of traces to skip
    :param gain: scaling factor for the traces
    :param lwidth: width of line
    :param xax: scaler of axis to match image plot
    """  
  

    t = (np.arange(data.shape[0]) * dt * 1000) + tstart

    # Need to resample this time axis to the same size as data.shape[1]

    for i in range(0,data.shape[1],skipt+1):

        trace = data[:,i]
        
        trace[0]=0      # make trace start at zero
        trace[-1]=0     # make trace end at zero
        
        new_trace = gain*(trace/np.amax(data))   # gain

        scaler = (np.amax(xax)-np.amin(xax))/float( len(xax)) # scale for window     
        
        quadrant.plot( (i + new_trace) * scaler + min(xax), t, color=line_colour, 
                  linewidth = lwidth, alpha = opacity)
                
        quadrant.fill_betweenx(t, ((i + new_trace) * scaler)+min(xax), (i * scaler)+min(xax) ,  new_trace > 0,
                         color=fill_colour, alpha=opacity, lw=0)
                
        quadrant.axis('tight')

def modelr_plot(model, colourmap, args):
    """
Calculates reflectivities from the earth model then convolves
against a bank of wavelets. Figures of various slices are created
based on the args structure.

:param model: The earth model image to use for forward modeling.
:param colourmap: A Dict that maps colour values in the earth
model to physical rock properties.
:param args: Structure of parsed arguments.

:returns: a png graphic of the forward model results.
"""

    from modelr.constants import dt, wavelet_duration as duration
    model_aspect = float(model.shape[1]) / model.shape[0]

    if not hasattr(args, 'xscale'):
        args.xscale = 0
    
    if not hasattr(args, "twt_range"):
        args.twt_range = (0, model.shape[0] * dt * 1000.0)
    
    if not hasattr(args, 'fs'):
        args.fs = 10
    
    if args.slice == 'spatial':
        traces = range( args.ntraces )
    else:
        traces = args.trace - 1
        if traces >= args.ntraces:
            traces = args.ntraces -1
        
    if args.slice == 'angle':
        theta0 = args.theta[0]
        theta1 = args.theta[1]
        
        try:
            theta_step = args.theta[2]
        except:
            theta_step = 1
        
        
        theta = np.linspace(theta0, theta1,
                            int((theta1-theta0) / theta_step))
        

    else:
        try:
            theta = args.theta[0]
        except:
            theta = args.theta
    
    if args.slice == 'frequency':
        f0 = args.f[0]
        f1 = args.f[1]
        
        try:
            f_step = args.f[2]
        except:
            f_step = 1
        
        if (args.xscale) == 0:
            f = np.linspace(f0, f1, (int((f1-f0)/f_step)) )
        else:
            f = np.logspace(max(np.log2(f0),np.log2(7)),np.log2(f1),300,endpoint=True, base=2.0)
    else:
        f = args.f


    tstart = args.twt_range[0]
    fs = int(args.fs)
     
    model = model[:, traces, :]
    model = np.reshape(model, (model.shape[0], np.size(traces),3))

    
    ############################
    # Get reflectivities
    reflectivity = get_reflectivity( data=model,
                                     colourmap=colourmap,
                                     theta=theta,
                                     reflectivity_method = \
                                       args.reflectivity_method
                                    )

    # Do convolution
    if ( ( duration / dt ) > ( reflectivity.shape[0] ) ):
        duration = reflectivity.shape[0] * dt
    wavelet = args.wavelet( duration, dt, f )
    if( wavelet.ndim == 1 ): wavelet = \
      wavelet.reshape( ( wavelet.size, 1 ) )
     
    warray_amp = do_convolve( wavelet, reflectivity )

    nsamps, ntraces, ntheta, n_wavelets = warray_amp.shape

    dx = 10 #trace offset (in metres)
    
    #################################
    # Build the plot(s)
       
    # Simplify the plot request a bit
    # This will need to be a loop if we want to cope with
    # an arbitrary number of base plots; or allow up to 6 (say)
    
    base1 = args.base1
    
    if args.overlay1 == 'none':
        overlay1 = None
    else:
        overlay1 = args.overlay1
    
    if args.overlay2 == 'none':
        overlay2 = None
    else:
        overlay2 = args.overlay2
        
    if args.base2 == 'none':
        base2 = None
        plots = [(base1, overlay1)]
        
    else:
        base2 = args.base2
        plots = [(base1, overlay1), (base2, overlay2)]

    if( args.slice == 'spatial' ):
        
        plot_data = warray_amp[ :, :, 0,:]
        reflectivity = reflectivity[:,:,0]
        xax = traces
        xlabel = 'trace'
    elif( args.slice == 'angle' ):
        plot_data = warray_amp[ :, 0, :, 0 ]
        reflectivity = reflectivity[ :, 0, : ]
        xax = theta
        xlabel = 'angle'
    elif( args.slice == 'frequency' ):
        plot_data = warray_amp[ :, 0, 0, : ]
        reflectivity = np.reshape( np.repeat( reflectivity[:,0,0],
                                              warray_amp.shape[1] ),
                                   ( reflectivity.shape[0],
                                     warray_amp.shape[1] ) )
        
        xax = f
        xlabel = 'frequency [Hz]'
    else:
        # Default to spatial
        plot_data = warray_amp[ :, :, 0, 0 ]

    # Calculate some basic stuff
    plot_data = np.nan_to_num(plot_data)
    
    # This doesn't work well for non-spatial slices
    #aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]
    
    # This is *better* for non-spatial slices, but can't have
    # overlays
    
    stretch = args.aspect_ratio
    
    pad = np.ceil((plot_data.shape[0] - model.shape[0]) / 2)

    # First, set up the matplotlib figure
    #fig = plt.figure(figsize=(width, 2*height))

    fig, axarr = plt.subplots(2, len(plots)) #, sharex='col', sharey='row')
    
    if len(plots) == 1:
        axarr = np.transpose(np.array([axarr]))
    
    # Work out the size of the figure
    each_width = 6
    fig.set_figwidth(each_width*len(plots))
    fig.set_figheight(each_width*stretch*2)

    # Start a loop for the figures...
    for plot in plots:
        
        # If there's no base plot for this plot,
        # then there are no more plots and we're done
        if not plot[0]:
            break
            
        # Establish what sort of subplot grid we need
        p = plots.index(plot)
    
        if args.xscale:
            axarr[0, p].set_xscale('log', basex = int(args.xscale) )
        
        # Each plot can have two layers (maybe more later?)
        # Display the two layers by looping over the non-blank
        # elements
        # of the tuple
        for layer in filter(None, plot):
            
            # for starters, find out if this is a base or an overlay
            if plot.index(layer) == 1:
                # then we're in an overlay so...
                alpha = args.opacity
            else:
                alpha = 1.0
            
            # Now find out what sort of plot we're making on this
            # loop...
            if layer == 'earth-model':
                axarr[0, p].imshow(model.astype('uint8'),
                          cmap = plt.get_cmap('gist_earth'),
                          vmin = np.amin(model)-np.amax(model)/2,
                          vmax = np.amax(model)+np.amax(model)/2,
                          alpha = alpha,
                          aspect='auto',
                          extent=[min(xax),max(xax),
                                   args.twt_range[1],
                                   args.twt_range[0]
                                 ],
                          origin = 'upper'
                           )
            
            elif layer == 'variable-density':
                vddata=plot_data
                if vddata.ndim == 3:
                    vddata = np.sum(plot_data,axis=-1)
                extreme = np.percentile(vddata,99)
            
                axarr[0, p].imshow( vddata,
                           cmap = args.colourmap,
                           vmin = -extreme,
                           vmax = extreme,
                           alpha = alpha,
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   args.twt_range[1],
                                   args.twt_range[0]
                                   ],
                           origin = 'upper'
                           )
                
    
            elif layer == 'reflectivity':
                # Show unconvolved reflectivities
                #
                #TO DO:put transparent when null / zero
                #
                masked_refl = np.ma.masked_where(reflectivity == 0.0,
                                                 reflectivity)
            
                axarr[0,p].imshow(masked_refl,
                           cmap = plt.get_cmap('Greys'),
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   args.twt_range[1], args.twt_range[0]
                                   ],
                           origin = 'upper' ,
                           vmin = np.amin( masked_refl ),
                           vmax = np.amax( masked_refl )
                           )

            elif layer == 'wiggle':
                
                wigdata=plot_data
                if wigdata.ndim == 3:
                    wigdata= np.sum(plot_data,axis=-1)
                wiggle(wigdata, 
                       tstart = int(args.twt_range[0]),
                       dt = dt,
                       skipt = args.wiggle_skips,
                       gain = args.wiggle_skips + 1,
                       line_colour = 'black',
                       fill_colour = 'black',
                       opacity = args.opacity,
                       xax = xax,
                       quadrant = axarr[0, p]
                       )
                if plot.index(layer) == 0:
                    # then we're in an base layer so...
                    axarr[0, p].set_ylim(max(axarr[0, p].set_ylim()),min(axarr[0, p].set_ylim()))

            elif layer == 'RGB':
                exponent = 2
                envelope = abs(hilbert(plot_data))
                envelope = envelope**exponent
                
                envelope[:,:,0]= envelope[:,:,0]/np.amax(envelope[:,:,0])
                envelope[:,:,1]= envelope[:,:,1]/np.amax(envelope[:,:,1])
                envelope[:,:,2]= envelope[:,:,2]/np.amax(envelope[:,:,2])
                
                extreme = np.amax(abs(envelope))
                axarr[0, p].imshow(envelope,
                           cmap = args.colourmap,
                           vmin = -extreme,
                           vmax = extreme,
                           alpha = alpha,
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   args.twt_range[1], args.twt_range[0]
                                   ],
                           origin = 'upper'
                           )
            else:
                # We should never get here
                continue
             
        axarr[0, p].set_xlabel(xlabel, fontsize=fs)
        axarr[0, p].set_ylabel('time [ms]', fontsize=fs)
        axarr[0, p].set_title(args.title % locals(), fontsize=fs )
        
        for tick in axarr[0,p].xaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
        
        for tick in axarr[0,p].yaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
        
        #plot inst. amplitude at 150 ms (every 6 samples, we should parameterize)
        t = args.tslice
        t_index = int(np.amin([t, plot_data.shape[0]-1]))
        y = plot_data[t_index,:].flatten()
        
        
        
        # compute lines for instantaneous chart
        amax_tune = np.amax(y)
        amin_tune = np.amin(y)
        aun_tuned = plot_data[t_index,-1]

        # instantaneous charts
        axarr[1,p].plot(xax[:],y,'ko-',lw=3,alpha=0.2, color = 'g')
        if args.xscale: #check for log plot on graphs too
            axarr[1, p].set_xscale('log', basex = int(args.xscale) )
        axarr[1,p].set_xlabel(xlabel, fontsize=fs)
        
        # horizontal line, plot min, plot max
        axarr[1, p].axhline(y=amin_tune, alpha=0.15, lw=3, color = 'g')
        axarr[1, p].axhline(y=amax_tune, alpha=0.15, lw=3, color = 'g' )
        
        #plot ave
        axarr[1, p].axhline(y=aun_tuned, alpha=0.15, lw=3, color = 'g')
        
        # vertical line
        axarr[1, p].axvline(x=xax[np.argmax(y)], alpha=0.15, lw=3, color='b' )
        axarr[1, p].axvline(x=xax[np.argmin(y)], alpha=0.15, lw=3, color='b' )
        axarr[0, p].axvline(x=xax[np.argmax(y)], alpha=0.15, lw=3, color='b' )
        axarr[0, p].axvline(x=xax[np.argmin(y)], alpha=0.15, lw=3, color='b' )
        # draw vertical line at onset of steady state
        y_r = np.array(y[::-1])
    
        try:
            steady_state = np.where(abs(np.gradient(y_r)) >= (0.001*np.ptp(y)))[0][0]
            axarr[1, p].axvline(x=xax[-steady_state], alpha=0.15, lw=3, color='r' )
            axarr[0, p].axvline(x=xax[-steady_state], alpha=0.15, lw=3, color='r' )
        except:
            pass
        #labels
        axarr[1, p].set_title('instantaneous attribute at %s ms' % int(t),
                               fontsize=fs
                              )
        axarr[1, p].set_ylabel('amplitude', fontsize=fs)
        axarr[1,p].grid()
        
        for tick in axarr[1,p].xaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
        
        for tick in axarr[1,p].yaxis.get_major_ticks():
            tick.label.set_fontsize(fs)
             
        plt.xlim((xax[0], xax[-1]))
        
        #plot horizontal green line on model image, and steady state
        axarr[0,p].axhline(y=t, alpha=0.5, lw=2, color = 'g')
        

    fig.tight_layout()

    
    return get_figure_data()

def multi_plot(model, reflectivity, seismic, traces,
               f, theta, args):
    """
    Calculates reflectivities from the earth model then convolves
    against a bank of wavelets. Figures of various slices are created
    based on the args structure.

    :param model: The earth model image to use for forward modeling.
    :param args: Structure of parsed arguments.

    :returns: a png graphic of the forward model results.
    """


    from modelr.constants import dt, wavelet_duration as duration

    model_aspect = float(model.shape[1]) / model.shape[0]

    # Do convolution
    if ( ( duration / dt ) > ( reflectivity.shape[0] ) ):
        duration = reflectivity.shape[0] * dt

    nsamps, ntraces, ntheta, n_wavelets = seismic.shape

    dx = 10    #trace offset (in metres)
    
    #################################
    # Build the plot(s)
       
    # Simplify the plot request a bit
    # This will need to be a loop if we want to cope with
    # an arbitrary number of base plots; or allow up to 6 (say)
    
    base1 = args.base1
    
    if args.overlay1 == 'none':
        overlay1 = None
    else:
        overlay1 = args.overlay1
    
    if args.overlay2 == 'none':
        overlay2 = None
    else:
        overlay2 = args.overlay2
        
    if args.base2 == 'none':
        base2 = None
        plots = [(base1, overlay1)]
        
    else:
        base2 = args.base2
        plots = [(base1, overlay1), (base2, overlay2)]

    if( args.slice == 'spatial' ):
        
        plot_data = seismic[ :, :, 0,:]
        reflectivity = reflectivity[:,:,0]
        xax = traces
        xlabel = 'trace'
    elif( args.slice == 'angle' ):
        plot_data = seismic[ :, 0, :, 0 ]
        reflectivity = reflectivity[ :, 0, : ]
        xax = theta
        xlabel = 'angle'
    elif( args.slice == 'frequency' ):
        plot_data = seismic[ :, 0, 0, : ]
        reflectivity = np.reshape( np.repeat( reflectivity[:,0,0],
                                              seismic.shape[1] ),
                                   ( reflectivity.shape[0],
                                     seismic.shape[1] ) )
        
        xax = f
        xlabel = 'frequency [Hz]'
    else:
        # Default to spatial
        plot_data = seismic[ :, :, 0, 0 ]

    # Calculate some basic stuff
    plot_data = np.nan_to_num(plot_data)
    
    # This doesn't work well for non-spatial slices
    #aspect = float(seismic.shape[1]) / seismic.shape[0]                                        
    
    # This is *better* for non-spatial slices, but can't have
    # overlays
    
    stretch  = args.aspect_ratio
    
    pad = np.ceil((plot_data.shape[0] - model.shape[0]) / 2)

    # First, set up the matplotlib figure
    #fig = plt.figure(figsize=(width, 2*height))

    fig, axarr = plt.subplots(2, len(plots))     #, sharex='col', sharey='row')
    
    if len(plots) == 1:
        axarr = np.transpose(np.array([axarr]))
    
    # Work out the size of the figure
    each_width = 6
    fig.set_figwidth(each_width*len(plots))
    fig.set_figheight(each_width*stretch*2)

    # Start a loop for the figures...
    for p, plot in enumerate(plots):
        
        # If there's no base plot for this plot,
        # then there are no more plots and we're done
        if not plot[0]:
            break
    
        if args.slice == "frequency" and args.xscale:
            if args.xscale=='octave':
                axarr[0, p].set_xscale('log', basex=int(2))    
        
        # Each plot can have two layers (maybe more later?)
        # Display the two layers by looping over the non-blank
        # elements
        # of the tuple
        for layer in filter(None, plot):
            
            # for starters, find out if this is a base or an overlay
            if plot.index(layer) == 1:
                # then we're in an overlay so...
                alpha = args.opacity
            else:
                alpha = 1.0
            
            # Now find out what sort of plot we're making on this
            # loop...        
            if layer == 'earth-model':
                
                axarr[0, p].imshow(model.astype('int'),
                          #cmap = plt.get_cmap('gist_earth'),
                          #vmin = np.amin(model)-np.amax(model)/2,
                          #vmax = np.amax(model)+np.amax(model)/2,
                          alpha = alpha,
                          aspect='auto',
                          extent=[min(xax),max(xax),
                                   args.twt_range[1], args.twt_range[0]
                                   ],
                          origin = 'upper'  
                           )
            
            elif layer == 'variable-density':
                vddata=plot_data
                if vddata.ndim == 3:
                    vddata = np.sum(plot_data,axis=-1)

                #for "scalar tuple (scale, clip percentage)
                if len(args.scale) == 1:
                    args.scale.append(99)
                if args.scale[0] == 0:
                    extreme = np.percentile(vddata, float(args.scale[1]))
                else:    
                    extreme = float(args.scale[0])
                
                im = axarr[0, p].imshow( vddata,

                           cmap = args.colourmap,
                           vmin = -extreme,
                           vmax = extreme,
                           alpha = alpha,
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   args.twt_range[1], args.twt_range[0]], 
                           origin = 'upper'
                           )         
                                              
                # Put colorbar legend
                colorbar_ax = fig.add_axes([(0.045*p) + 0.9*( float((p+1)) / len(plots) ), 0.875, 0.03/len(plots), 0.07])
                fig.colorbar(im, cax=colorbar_ax)
                colorbar_ax.text( 0.5, -0.1, '%3.2f' % -extreme, transform=colorbar_ax.transAxes, horizontalalignment='center',verticalalignment='top')
                colorbar_ax.text(0.5, 1.1, '%3.2f' % extreme, transform=colorbar_ax.transAxes, horizontalalignment='center')
                colorbar_ax.set_axis_off()
                    
    
            elif layer == 'reflectivity':
                # Show unconvolved reflectivities
                #
                #TO DO:put transparent when null / zero
                #
                masked_refl = np.ma.masked_where(reflectivity == 0.0,
                                                 reflectivity)
            
                axarr[0,p].imshow(masked_refl,
                           cmap = plt.get_cmap('Greys'),
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   args.twt_range[1], args.twt_range[0]
                                   ],
                           origin = 'upper' ,
                           vmin = np.amin( masked_refl ),
                           vmax = np.amax( masked_refl )
                           )

            elif layer == 'wiggle':
            # wiggle needs an alpha setting too
                wigdata=plot_data
                if wigdata.ndim == 3:
                    wigdata= np.sum(plot_data,axis=-1)
                wiggle(wigdata, 
                       tstart = int(args.twt_range[0]), 
                       dt = dt,
                       skipt = args.wiggle_skips,
                       gain = args.wiggle_skips + 1,
                       line_colour = 'black',
                       fill_colour = 'black',
                       opacity = args.opacity,
                       xax = xax,
                       quadrant = axarr[0, p]
                       )    
                if plot.index(layer) == 0:
                    # then we're in an base layer so...
                    axarr[0, p].set_ylim(max(axarr[0, p].set_ylim()),min(axarr[0, p].set_ylim()))

            elif layer == 'RGB':
                exponent = 2
                envelope = abs(hilbert(plot_data))
                envelope = envelope**exponent
                
                envelope[:,:,0]= envelope[:,:,0]/np.amax(envelope[:,:,0])
                envelope[:,:,1]= envelope[:,:,1]/np.amax(envelope[:,:,1])
                envelope[:,:,2]= envelope[:,:,2]/np.amax(envelope[:,:,2])
                
                extreme = np.amax(abs(envelope))
                axarr[0, p].imshow(envelope,
                           cmap = args.colourmap,
                           vmin = -extreme,
                           vmax = extreme,
                           alpha = alpha,
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   args.twt_range[1], args.twt_range[0]
                                   ], 
                           origin = 'upper'
                           )
            else:
                # We should never get here
                continue   
            
        axarr[0, p].set_xlabel(xlabel, fontsize=fs)
        axarr[0, p].set_ylabel('time [ms]', fontsize=fs)
        axarr[0, p].set_title(args.title % locals(), fontsize=fs)
        
        for tick in axarr[0,p].xaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
        
        for tick in axarr[0,p].yaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
                
        #plot inst. amplitude at 150 ms (every 6 samples, we should parameterize)
        t = args.tslice
        t_index = int(np.amin([t, plot_data.shape[0]-1]))
        y = plot_data[t_index,:].flatten()
        
        
        
        # compute lines for instantaneous chart
        amax_tune = np.amax(y)
        amin_tune = np.amin(y)
        aun_tuned = plot_data[t_index,-1]

        # instantaneous charts       
        axarr[1,p].plot(xax[:],y,'ko-',lw=3,alpha=0.2, color = 'g')
        if args.xscale and args.slice=="frequency":    #check for log plot on graphs too
            if args.xscale=='octave':
                axarr[1, p].set_xscale('log', basex=2)
        axarr[1,p].set_xlabel(xlabel, fontsize=fs)
        
        # horizontal line, plot min, plot max
        axarr[1, p].axhline(y=amin_tune, alpha=0.15, lw=3, color = 'g')
        axarr[1, p].axhline(y=amax_tune, alpha=0.15, lw=3, color = 'g' )
        
        #plot ave
        axarr[1, p].axhline(y=aun_tuned, alpha=0.15, lw=3, color = 'g')
        
        # vertical line
        axarr[1, p].axvline(x=xax[np.argmax(y)], alpha=0.15, lw=3, color='b' )
        axarr[1, p].axvline(x=xax[np.argmin(y)], alpha=0.15, lw=3, color='b' )
        axarr[0, p].axvline(x=xax[np.argmax(y)], alpha=0.15, lw=3, color='b' )
        axarr[0, p].axvline(x=xax[np.argmin(y)], alpha=0.15, lw=3, color='b' )
        # draw vertical line at onset of steady state
        y_r = np.array(y[::-1])
        try:
            steady_state = np.where(abs(np.gradient(y_r)) >= (0.001*np.ptp(y)))[0][0]
            axarr[1, p].axvline(x=xax[-steady_state], alpha=0.15, lw=3, color='r' )
            axarr[0, p].axvline(x=xax[-steady_state], alpha=0.15, lw=3, color='r' )
        except:
            pass
        #labels
        axarr[1, p].set_title('instantaneous attribute at %s ms' % int(t*1000.0),
                               fontsize=fs
                               )
        axarr[1, p].set_ylabel('amplitude', fs )
        axarr[1,p].grid()
        axarr[1,p].set_xlim(xax[0], xax[-1])
        
        for tick in axarr[1,p].xaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
        
        for tick in axarr[1,p].yaxis.get_major_ticks():
            tick.label.set_fontsize(fs) 
        
        #plot horizontal green line on model image, and steady state
        axarr[0,p].axhline(y=t, alpha=0.5, lw=2, color = 'g')

    fig.tight_layout()

    return get_figure_data()



    

    
    
if __name__ == '__main__':
    dt =0.001
    gain = 1
    temp = ricker(0.256,dt,25)
    ntraces=50
    data =np.zeros((temp.shape[0],ntraces))

    for i in range(ntraces):
        temp = ricker(0.256,dt,25+10*i)
        data[:,i] = temp
    
    wiggle(data,dt,skipt=1,gain=gain)  
