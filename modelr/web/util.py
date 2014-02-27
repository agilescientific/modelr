'''
==================
modelr.web.util
==================

Created on May 3, 2012

@author: sean
'''

import tempfile
import matplotlib
import matplotlib.pyplot as plt
from agilegeo.wavelet import ricker
import numpy as np
from modelr.reflectivity import get_reflectivity, do_convolve

def get_figure_data(transparent=False):
    '''
    Return the current plot as a binary blob. 
    '''
    fig_path = tempfile.NamedTemporaryFile(suffix='.png', delete=True)
    plt.savefig(fig_path.name, transparent=transparent)
    plt.close()
    with open(fig_path.name, 'rb') as fd:
        data = fd.read()
             
        
    # Alternative approach to do it in memory rather than on disk
    #image_file = tempfile.SpooledTemporaryFile(suffix='.png')
    #plt.savefig(image_file, format='png') 
    #data = image_file.read()
    
    return data

def wiggle(data, dt=1, line_colour='black', fill_colour='blue',
           opacity= 0.5, skipt=0, gain=1, lwidth=.5, xax=1):
    """
    Make a wiggle trace and plots it on the current figure.
    
    :param data: as a 2D array indexed as [samples, traces]      
    :param dt: sample interval of the data [seconds].
    :param skipt: number of traces to skip
    :param gain: scaling factor for the traces
    :param lwidth: width of line
    :param xax: scaler of axis to match image plot
    """  
  
    t = np.arange(data.shape[0])*dt
    for i in range(0,data.shape[1],skipt+1):

        trace = data[:,i]
        
        trace[0]=0
        trace[-1]=0 
        new_trace = gain*(trace/np.amax(data))

        scaler = (np.amax(xax)-np.amin(xax))/float( len(xax))
    
        plt.plot( (i + new_trace) * scaler + min(xax), t, color=line_colour, 
                linewidth=lwidth,alpha=opacity)
    
        plt.fill_betweenx(t, ((i + new_trace) * scaler)+min(xax), (i * scaler)+min(xax) ,  new_trace > 0,
                          color=fill_colour, alpha=opacity, lw=0)
    
    plt.axis('tight')

def modelr_plot( model, colourmap, args ):
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

    from modelr.constants import dt, duration
    model_aspect = float(model.shape[1]) / model.shape[0]

    if args.slice == 'spatial':
        traces = range( args.ntraces )
    else:
        traces = args.trace - 1
        
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
        
        f = np.linspace(f0, f1, (int((f1-f0)/f_step)) )
        
    else:
        f = args.f


    model = model[:, traces, :]
    model = np.reshape( model, (model.shape[0], np.size(traces),3) )

    
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
        plot_data = warray_amp[ :, :, 0,0]
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
        xlabel = 'frequency'
    else:
        # Default to spatial
        plot_data = warray_amp[ :, :, 0, 0 ]

    # Calculate some basic stuff
    
    # This doesn't work well for non-spatial slices
    #aspect = float(warray_amp.shape[1]) / warray_amp.shape[0]                                        
    
    # This is *better* for non-spatial slices, but can't have
    # overlays
    
    stretch  = args.aspect_ratio
    
    pad = np.ceil((plot_data.shape[0] - model.shape[0]) / 2)

    # Work out the size of the figure
    each_width = 5
    width = each_width*len(plots)
    height = each_width*stretch

    # First, set up the matplotlib figure
    fig = plt.figure(figsize=(width, height))

    
    # Start a loop for the figures...
    for plot in plots:
        
        # If there's no base plot for this plot,
        # then there are no more plots and we're done
        if not plot[0]:
            break
            
        # Establish what sort of subplot grid we need
        l = len(plots)
        p = plots.index(plot)
                
        # Set up the plot 'canvas'
        ax = fig.add_subplot(1,l,p+1)
            
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
                ax.imshow(model,
                          cmap = plt.get_cmap('gist_earth'),
                          vmin = np.amin(model)-np.amax(model)/2,
                          vmax = np.amax(model)+np.amax(model)/2,
                          alpha = alpha,
                          aspect='auto',
                          extent=[min(xax),max(xax),
                                   plot_data.shape[0]*dt,0],
                          origin = 'upper'  
                           )
            
            elif layer == 'variable-density':
                
                ax.imshow(plot_data,
                           cmap = args.colourmap,
                           alpha = alpha,
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   plot_data.shape[0]*dt,0], 
                           origin = 'upper'
                           )
    
            elif layer == 'reflectivity':
                # Show unconvolved reflectivities
                #
                #TO DO:put transparent when null / zero
                #
                masked_refl = np.ma.masked_where(reflectivity == 0.0, reflectivity)
            
                ax.imshow(masked_refl,
                           cmap = plt.get_cmap('Greys'),
                           aspect='auto',
                           extent=[min(xax),max(xax),
                                   plot_data.shape[0]*dt,0],
                           origin = 'upper' ,
                           vmin = np.amin( masked_refl ),
                           vmax = np.amax( masked_refl )
                           )

            elif layer == 'wiggle':
            # wiggle needs an alpha setting too
                wiggle(plot_data,
                       dt = dt,
                       skipt = args.wiggle_skips,
                       gain = args.wiggle_skips + 1,
                       line_colour = 'black',
                       fill_colour = 'black',
                       opacity = args.opacity,
                       xax = xax
                       )    
                if plot.index(layer) == 0:
                    # then we're in an base layer so...
                    ax.set_ylim(max(ax.set_ylim()),min(ax.set_ylim()))

            else:
                # We should never get here
                continue     
        ax.set_xlabel(xlabel)
        ax.set_ylabel('time [s]')
        ax.set_title(args.title % locals())
 
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
