'''
================================================================
modelr.reflectivity -- TODO short docstring here
================================================================

Basic methods for creating models.

'''
import numpy as np
import scipy
from modelr.web.urlargparse import WAVELETS
from agilegeo import avo as reflection

###################
# New style functions

def zoeppritz(Rp0, Rp1, theta1):
    '''
    Wrapper around long zoeppritz funcion.
    
    :param Rp0:
    :param Rp1:
    :param theta1:
     
    '''
    return reflection.zoeppritz(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)    

def akirichards(Rp0, Rp1, theta1):
    reflection.akirichards(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def akirichards_alt(Rp0, Rp1, theta1):
    reflection.akirichards_alt(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def fatti(Rp0, Rp1, theta1):
    reflection.fatti(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def shuey2(Rp0, Rp1, theta1):
    reflection.shuey2(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def shuey3(Rp0, Rp1, theta1):
    reflection.shuey3(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def bortfeld2(Rp0, Rp1, theta1):
    reflection.bortfeld2(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)
    
def bortfeld3(Rp0, Rp1, theta1):
    reflection.bortfeld3(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

MODELS = {
             'zoeppritz': zoeppritz,
             'akirichards': akirichards,
             'akirichards_alt': akirichards_alt,
             'fatti': fatti,
             'shuey2': shuey2,
             'shuey3': shuey3,
             'bortfeld2': reflection.bortfeld2,
             'bortfeld3': reflection.bortfeld3,
             }

FUNCTIONS = {
             'zoeppritz': reflection.zoeppritz,
             'akirichards': reflection.akirichards,
             'akirichards_alt': reflection.akirichards_alt,
             'fatti': reflection.fatti,
             'shuey2': reflection.shuey2,
             'shuey3': reflection.shuey3,
             'bortfeld2': reflection.bortfeld2, 
             'bortfeld3': reflection.bortfeld3,
             }

def get_reflectivity(data,
                     colourmap,
                     theta=0,
                     reflectivity_method='zoeppritz',
                     ):
    '''
    Create reflectivities from model.
    
    :param data: the physical model to use
    :param theta: angle of incidence
    :param reflectivity_method: the reflectivity algorithm to use
    '''

    array_amp = np.zeros( data.shape )

    # Make an array that only has the boundaries in it
    # This is a hack to reduce the number of times we call
    # reflectivity_method
    boundaries = np.diff(data, axis=0)
    # Note that this array has one less row than data array,
    # the first row is 'missing'
    
    # Now iterate over this array, with index flags turned on
    # If we hit a non-zero value, we need to get the reflectivity
    # Pretty gross, but it works
    i = np.nditer(boundaries, flags=['multi_index'])
    while not i.finished:
        if i[0] != 0:
            # These are the indices in data
            sample = i.multi_index[0]
            trace = i.multi_index[1]
            array_amp[sample,trace] = \
                reflectivity_method(colourmap[data[sample,trace]],
                                    colourmap[data[sample+1,trace]],
                                    theta)
        i.iternext()

    return array_amp

def do_convolve(wavelet,f,array_amp,dt=0.001,traces=None):
    
    if traces == None:
        traces = array_amp.shape[1]
    
    duration = 0.2
    w = wavelet(duration,dt, f)
    
    samples = max(array_amp.shape[0], w.shape[0])
    
    warray_amp = np.zeros([samples, traces])
    
    for i in range(traces):
        warray_amp[:, i] = np.convolve(array_amp[:, i], w, mode='same')
        
    return np.array(warray_amp)

####################
# Old model-building functions

def create_wedge(ntraces, pad, max_thickness, prop0, prop1, 
                 prop2=None, theta=0, wavelet=WAVELETS['ricker'],
                 f=25,reflectivity_method=MODELS['zoeppritz'],
                 dt=0.001):
    '''
    Create a wedge model.
    
    :param ntraces: number of traces
    :param pad: pad the array top and bottom in ms
    :param max_thickness: The thickest part of the wedge
    :param prop0: rock properties, top layer
    :param prop1: rock properties, middle layer
    :param prop2: rock properties, bottom layer
    :param theta: angle of incidence
    :param f: the frequency for the wavelet
    '''
    
    if prop2 == None or prop2=='':
        prop2 = prop0
    
    scale = 10
    nsamples = (2 * pad + max_thickness) * scale
      
    array_amp = np.zeros([nsamples, ntraces])
    fwedge = np.floor(np.linspace(pad * scale,
                                 (pad + max_thickness) * scale,
                      ntraces, endpoint=False))
    wedge = np.array(fwedge, dtype=int)

    Rp0 = reflectivity_method(prop0.vp, prop0.vs, prop0.rho,
                              prop1.vp, prop1.vs, prop1.rho, theta)
    Rp1 = reflectivity_method(prop1.vp, prop1.vs, prop1.rho,
                              prop2.vp, prop2.vs, prop2.rho, theta)
    
    array_amp[pad * scale, :] += Rp0
    array_amp[wedge, np.arange(ntraces)] += Rp1
            
    result = do_convolve(wavelet, f,array_amp, dt)
    
    return result

def create_tilted(ntraces, pad, max_thickness, prop0, prop1,
                  prop2=None, theta=0, wavelet=WAVELETS['ricker'],
                  f=25,reflectivity_method=MODELS['zoeppritz'],
                  dt=0.001):
    '''
    Create a tilted model.
    
    :param ntraces: number of traces
    :param pad: pad the array top and bottom in ms
    :param max_thickness: The thickest part of the wedge
    :param prop0: rock properties, top layer
    :param prop1: rock properties, middle layer
    :param prop2: rock properties, bottom layer
    :param theta: angle of incidence
    :param f: the frequency for the wavelet
    '''
    
    if prop2 == None or prop2=='':
        prop2 = prop0
    
    scale = 10
    nsamples = (2 * pad + max_thickness) * scale
      
    fwedge = np.floor(np.linspace(0.25*pad*scale,
                                  (pad+max_thickness) * scale,
                                  ntraces,
                                  endpoint = False
                                  )
                      )
                      
    twedge = np.array(fwedge, dtype=int)

    fwedge = np.floor(np.linspace(1.25*pad * scale,
                                  (2*pad + max_thickness) * scale,
                                  ntraces,
                                  endpoint = False
                                  )
                      )
                      
    bwedge = np.array(fwedge, dtype=int)

    Rp0 = reflectivity_method(prop0.vp, prop0.vs, prop0.rho,
                              prop1.vp, prop1.vs, prop1.rho, theta)
    Rp1 = reflectivity_method(prop1.vp, prop1.vs, prop1.rho,
                              prop2.vp, prop2.vs, prop2.rho, theta)
    
    array_amp = np.zeros([nsamples, ntraces])
    array_amp[ twedge, np.arange(ntraces)] += Rp0
    array_amp[ bwedge, np.arange(ntraces)] += Rp1
            
    result = do_convolve(wavelet, f, array_amp, dt)
    
    return result

def create_theta(pad, thickness, prop0, prop1,
                 theta, wavelet=WAVELETS['ricker'], f=25, dt=0.001,
                 reflectivity_method=MODELS['zoeppritz']):
    '''
    Create a 2D array where the first dimension is time
    and the second is angle.

    :param pad: pad the array top and bottom in ms
    :param thickness: the distanc between the two interfaces
    :param prop0: rock properties 1
    :param prop1: rock properties 1
    :param theta: array of angles
    :param f: the frequency for the wavelet
    '''
    
    nsamples = (2 * pad + thickness)
      
    array_amp = np.zeros([nsamples, theta.size])
        
    Rp0 = reflectivity_method(prop0.vp, prop0.vs,
                              prop0.rho, prop1.vp, prop1.vs,
                              prop1.rho, theta)
    Rp1 = reflectivity_method(prop1.vp, prop1.vs, prop1.rho,
                              prop0.vp, prop0.vs, prop0.rho, theta)
    
    array_amp[pad, :] += Rp0
    array_amp[pad + thickness, :] += Rp1
    
    print "sending now"
    
    result = do_convolve(wavelet, f, array_amp, dt,
                         traces=theta.size)
    
    return result
    
def create_theta_spike(pad, prop0, prop1, theta, f,
                       duration,
                       reflectivity_method = MODELS['zoeppritz'],
                       wavelet = WAVELETS['ricker']):
    '''
    Create a 2D array where the first dimension is time and
    the second is angle.

    :param pad: pad the array top and bottom in ms
    :param prop0: rock properties 1
    :param prop1: rock properties 1
    :param theta: array of angles
    :param f: the frequency for the wavelet
    '''

    nsamples = (2 * pad)

    array_amp = np.zeros([nsamples, theta.size])

    Rp = reflectivity_method(prop0.vp, prop0.vs, prop0.rho,
                             prop1.vp, prop1.vs, prop1.rho, theta)
    array_amp[pad, :] += Rp

    result = do_convolve(wavelet,f, array_amp, traces=theta.size)
    
    return result
