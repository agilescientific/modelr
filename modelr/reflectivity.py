# -*- coding: utf-8 -*-
'''
================================================================
modelr.reflectivity -- TODO short docstring here
================================================================

Basic methods for creating models.

'''
import numpy as np
import scipy
from agilegeo import avo as reflection

###################
# New style functions
def rock_reflectivity( Rp0, Rp1, theta=0.0,
                       method=reflection.zoeppritz ):
    """
    A wrapper function for calling any of the reflection methods using
    rock property structures.

    :param Rp0: A rock properties structure for the top medium.
                Struct must contain vp, vs, rho.
    :param Rp1: A rock properties structure for the bottom medium.
                Struct must contain vp, vs, rho.
                
    :keyword theta: A single angle or an array of angles to calculate
                    angle dependent reflectivity. Defaults to 0.
    :keyword method: The reflectivity method to use. See agilegeo.avo
                     for available functions. Defaults to zoeppreitz.

    :returns the p-wave reflection coefficients for each value of
             theta.
    """

    return method( Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp,
                   Rp1.vs, Rp1.rho, theta )



def get_reflectivity(data,
                     colourmap,
                     theta=0,
                     reflectivity_method=reflection.zoeppritz
                     ):
    '''
    Create reflectivities from an image of an earth model and a
    mapping of colours to rock properties. Will find each interface
    and use the specified reflectivity method to calculate the Vp
    reflection coefficient.
    
    :param data: The image data of the earth model. A 2D array indexed
                 as [samples, traces].
    :param colourmap: A lookup table (dict) that maps colour values to
                      rock property structures.
    
    :keyword theta: Angle of incidence to use reflectivity. Can be a
                  float or an array of angles [deg].
    :keyword reflectivity_method: The reflectivity algorithm to use.
                                  See agilegeo.avo for methods.

    :returns The vp reflectivity coefficients corresponding to the
             earth model.
    '''

    if np.size(theta) > 1:
        array_shape = list(data.shape)
        array_shape.append(np.size(theta))
        array_amp = np.zeros(array_shape)

    else:
        array_amp = np.zeros( data.shape )

    # Make an array that only has the boundaries in it
    # This is a hack to reduce the number of times we call
    # reflectivity_method
    boundaries = np.where( np.diff(data, axis=0) )
    
    # Note that this array has one less row than data array,
    # the first row is 'missing'
    
    # Now iterate over this array, with index flags turned on
    i = np.nditer( boundaries,
                   flags=['multi_index'] )
    while not i.finished:
        
        # These are the indices in data
        sample = i.multi_index[0]
        next_sample = list(i.multi_index[:])
        next_sample[0] += 1
        next_sample = tuple(next_sample)
        
        ref = reflectivity_method( colourmap[data[i.multi_index]],
                                   colourmap[data[next_sample]],
                                   theta )
            
        if( np.size(theta) ==1 ):
            array_amp[i.multi_index] = ref
        else:
            array_amp[i.multi_index, :] = ref
                
        i.iternext()

    return array_amp

def do_convolve( wavelets, data,
                 traces=None ):
    """
    Convolves wavelets against a reflectivity dataset.

    :param wavelets: An array of wavelets to convolve with the
                     dataset. The array must be indexed as
                     [samples, wavelet].
    :param: data: An array of reflectivity data to convolve against.
                  Must be indexed as [samples, traces ].

    :keyword traces: Indexes of of traces to convolve. If none are
                     specified, convolutions will be calculated for
                     every trace.

    :returns an array of synthetic seismic traces, indexed as
             [samples, traces, wavelet]. 
    """

    nsamps = data.shape[0]
    
    if( traces == None ):
        traces = range( data.shape[1] )
        n_traces = traces.size
        data = np.reshape( data.shape[0], n_traces )
    
    if ( np.size( wavelets.shape ) > 1 ):
        n_wavelets = wavelets.shape[1]
    else:
        n_wavelets = 1
        wavelets = np.reshape( wavelets.size, n_wavelets )

    # Initialize the output
    output = np.zeros( (nsamps, traces.size, n_wavelets ) )

    # Loop through traces
    for trace in traces:
        # Loop through wavelets
        for wave in range( n_wavelets ):
            
            output[:,trace, wave] = \
              np.convolve( data[:,trace],
                           wavelet[:,wave],
                           mode='same')
    
    return (output)



