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
from itertools import product


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
    ref = method( Rp0.vp, Rp0.vs, Rp0.rho,
                  Rp1.vp, Rp1.vs, Rp1.rho,
                  theta )

    return ref



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
             earth model. Data will be indexed as
             [sample, trace, theta]
    '''

    if( data.ndim == 1 ):
        reflect_data = np.zeros( (data.size, 1, np.size( theta )) )
        data = np.reshape( data, ( data.size, 1 ) )
    else:
        reflect_data = np.zeros( ( data.shape[0], data.shape[1],
                                   np.size( theta ) ) )

    # Make an array that only has the boundaries in it
    boundaries = np.transpose(
        np.diff(data, axis=0).nonzero())

    
    # Note that this array has one less row than data array,
    # the first row is 'missing'
    for i in boundaries:

        # These are the indices in data
        j = i.copy()
        j[0] += 1
        reflect_data[i[0],i[1],:] = \
          rock_reflectivity( colourmap[data[ i[0],i[1] ]],
                             colourmap[data[j[0], j[1]]],
                             theta=theta,
                             method=reflectivity_method )

    
    return reflect_data

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
        traces = np.arange( data.shape[1] )
    ntraces = traces.size
    ntheta = data.shape[2]
    
    if ( wavelets.ndim  > 1 ):
        n_wavelets = wavelets.shape[1]
    else:
        n_wavelets = 1
        wavelets = np.reshape( wavelets.size, n_wavelets )

    # Initialize the output
    output = np.zeros( ( nsamps, ntraces, ntheta,
                         n_wavelets ) )


    for iters in \
      product( traces, range( ntheta), range( n_wavelets ) ):
      
        output[:,iters[0],iters[1], iters[2]] = \
            np.convolve( data[:,iters[0], iters[1]],
                              wavelets[:,iters[2]], mode='same')

    
    return (output)



