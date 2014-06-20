# -*- coding: utf-8 -*-
'''
=====================
modelr.reflectivity 
=====================

Basic methods for creating models.
'''

import numpy as np
import scipy
from agilegeo import avo as reflection
from itertools import product
from svgwrite import rgb

###################
# New style functions

def get_boundaries( data ):
    """
    Finds interfaces in the earth model

    :param data: A numpy array of RGB values, indexed as
                 (sample, trace, (R,G,B) )
    :returns: a list of indices where a boundary occurs.
    """
    
    diff = np.absolute( np.diff(data, axis=0) )
    d1 = np.sum(diff , axis=2 )
    boundaries = np.transpose(
        d1.nonzero())
    
    return( boundaries )

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

    :returns: the p-wave reflection coefficients for each value of
             theta.
    """
    ref = method(Rp0.vp, Rp0.vs, Rp0.rho,
                 Rp1.vp, Rp1.vs, Rp1.rho,
                 theta)

    return np.nan_to_num(ref)
    



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
    
    :param data: The image data of the earth model. A 3D array indexed
                 as [samples, traces, colour].
    :param colourmap: A lookup table (dict) that maps colour values to
                      rock property structures.
    
    :keyword theta: Angle of incidence to use reflectivity. Can be a
                  float or an array of angles [deg].
    :keyword reflectivity_method: The reflectivity algorithm to use.
                                  See agilegeo.avo for methods.

    :returns: The vp reflectivity coefficients corresponding to the
             earth model. Data will be indexed as
             [sample, trace, theta]
    '''

    # Check if we only have one trace of data, and reform the array
    if( data.ndim == 2 ):
        reflect_data = np.zeros((data.size, 1, np.size(theta)))
        data = np.reshape(data, (data.shape[0], 1, 3))
    else:
        reflect_data = np.zeros((data.shape[0], data.shape[1],
                                np.size(theta)))

    # Make an array that only has the boundaries in it
    boundaries = get_boundaries(data)

    for i in boundaries:

        # These are the indices in data
        j = i.copy()
        j[0] += 1

        # Get the colourmap dictionary keys
        c1 = rgb(data[ i[0],i[1],0 ],  data[i[0],i[1],1 ],
                  data[ i[0],i[1],2 ])
        c2 = rgb( data[ j[0],j[1],0 ],  data[j[0],j[1],1 ],
                  data[ j[0],j[1],2 ] )

        # Don't calculate if not in the cmap. If the model was
        # build properly this shouldn't happen.
        if( ( c1 not in colourmap ) or ( c2 not in colourmap ) ):
            continue

        # Get the reflectivity
        reflect_data[i[0],i[1],:] = \
          rock_reflectivity( colourmap[c1],
                             colourmap[c2],
                             theta=theta,
                             method=reflectivity_method )

    
    return reflect_data

def do_convolve(wavelets, data,
                traces=None, theta=None):
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

    :returns: an array of synthetic seismic traces, indexed as
             [samples, traces, wavelet]. 
    """

    if traces is None:
        traces = np.arange(data.shape[1])
    ntraces = np.size(traces)

    if ntraces==1:
        traces = [traces]
    

    if theta is None:
        theta = np.arange(data.shape[2])

    ntheta = np.size(theta)
    
    if (wavelets.ndim > 1):
        n_wavelets = wavelets.shape[1]
    else:
        n_wavelets = 1
        wavelets = wavelets[:, np.newaxis]
        

    # Check if we need zero padding
    if wavelets.shape[0] > data.shape[0]:
        pad = wavelets.shape[0]
        data = np.pad(data,((wavelets.shape[0], 0),(0,0),(0,0)),
                      mode='constant',
                      constant_values=((0,0),(0,0),(0,0)))
    else: pad = 0

    # Initialize the output
    output = np.zeros((data.shape[0], ntraces, ntheta,
                       n_wavelets))


    # Loop through each combination of wavelet, trace, and theta
    for iters in \
      product(range(np.size(traces)), range(ntheta),
              range(n_wavelets)):

        output[:,iters[0],iters[1], iters[2]] = \
            scipy.signal.fftconvolve( data[:,traces[iters[0]],
                                           iters[1]].flatten(),
                                      wavelets[:,iters[2]].flatten(),
                                      mode='same')
        

    return output[pad:, :,:,:]



