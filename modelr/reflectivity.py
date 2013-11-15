'''
================================================================
modelr.reflectivity -- TODO short docstring here
================================================================

Basic methods for creating models.

'''
import numpy as np
from modelr.rock_properties import zoeppritz
from agilegeo.wavelet import ricker

def do_convolve(ntraces,f,duration,array_amp,type=None):
    r = ricker(.2,duration, f)
    
    warray_amp = np.zeros([max(array_amp.shape[0], r.shape[0]), array_amp.shape[1]])
    
    for i in range(ntraces):
        warray_amp[:, i] = np.convolve(array_amp[:, i], r, mode='same')
    
    print "all done convolving"
        
    if not type:
        return np.array(warray_amp)
    else:
        scale = duration / 100
        return np.array(warray_amp[::scale, :])
    
def create_wedge(ntraces, pad, max_thickness, prop0, prop1, theta, f, reflectivity_method):
    '''
    Create a wedge model.
    
    :param ntraces: number of traces
    :param pad: pad the array top and bottom in ms
    :param max_thickness: The thickest part of the wedge
    :param prop0: rock properties 1
    :param prop1: rock properties 1
    :param theta: angle of incidence
    :param f: the frequency for the wavelet
    '''
    scale = 10
    nsamples = (2 * pad + max_thickness) * scale
      
    array_amp = np.zeros([nsamples, ntraces])
    fwedge = np.floor(np.linspace(pad * scale, (pad + max_thickness) * scale,
                      ntraces, endpoint=False))
    wedge = np.array(fwedge, dtype=int)

    Rp0 = reflectivity_method(prop0, prop1, theta)
    Rp1 = reflectivity_method(prop1, prop0, theta)
    
    array_amp[pad * scale, :] += Rp0
    array_amp[wedge, np.arange(ntraces)] += Rp1
    
    print "sending now"
        
    result = do_convolve(ntraces,f,100*scale,array_amp,type='wedge')
    
    return result

def create_theta(pad, thickness, prop0, prop1, theta, f, duration, reflectivity_method):
    '''
    Create a 2D array where the first dimension is time and the second is angle.

    :param pad: pad the array top and bottom in ms
    :param thickness: the distanc between the two interfaces
    :param prop0: rock properties 1
    :param prop1: rock properties 1
    :param theta: array of angles
    :param f: the frequency for the wavelet
    '''
    
    nsamples = (2 * pad + thickness)
      
    array_amp = np.zeros([nsamples, theta.size])
        
    Rp0 = reflectivity_method(prop0, prop1, theta)
    Rp1 = reflectivity_method(prop1, prop0, theta)
    
    array_amp[pad, :] += Rp0
    array_amp[pad + thickness, :] += Rp1
    
    print "sending now"
    
    result = do_convolve(theta.size,f,duration,array_amp)
    
    return result

    
def create_theta_spike(pad, prop0, prop1, theta, f, duration, reflectivity_method):
    '''
    Create a 2D array where the first dimension is time and the second is angle.

    :param pad: pad the array top and bottom in ms
    :param prop0: rock properties 1
    :param prop1: rock properties 1
    :param theta: array of angles
    :param f: the frequency for the wavelet
    '''

    nsamples = (2 * pad)

    array_amp = np.zeros([nsamples, theta.size])

    Rp = reflectivity_method(prop0, prop1, theta)
    array_amp[pad, :] += Rp

    result = do_convolve(theta.size,f,duration,array_amp)
    
    return result