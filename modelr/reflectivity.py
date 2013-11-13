'''
================================================================
modelr.reflectivity -- TODO short docstring here
================================================================

Basic methods for creating models.

'''
import numpy as np
from modelr.rock_properties import zoeppritz
from agilegeo.wavelet import ricker

def do_convolve(ntraces,f,dt,array_amp,type=None):
    duration = 0.2
    r = ricker(duration,dt, f)
    
    warray_amp = np.zeros([max(array_amp.shape[0], r.shape[0]), array_amp.shape[1]])
    
    for i in range(ntraces):
        warray_amp[:, i] = np.convolve(array_amp[:, i], r, mode='same')
    
    print "all done convolving"
        
    return np.array(warray_amp)

def create_wedge(ntraces, pad, max_thickness, prop0, prop1, prop2=None, theta=0, f=25, reflectivity_method='zoeppritz'):
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
    fwedge = np.floor(np.linspace(pad * scale, (pad + max_thickness) * scale,
                      ntraces, endpoint=False))
    wedge = np.array(fwedge, dtype=int)

    Rp0 = reflectivity_method(prop0, prop1, theta)
    Rp1 = reflectivity_method(prop1, prop2, theta)
    
    array_amp[pad * scale, :] += Rp0
    array_amp[wedge, np.arange(ntraces)] += Rp1
            
    result = do_convolve(ntraces,f,0.001,array_amp,type='wedge')
    
    return result

def create_tilted(ntraces, pad, max_thickness, prop0, prop1, prop2=None, theta=0, f=25, reflectivity_method='zoeppritz'):
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

    Rp0 = reflectivity_method(prop0, prop1, theta)
    Rp1 = reflectivity_method(prop1, prop2, theta)
    
    array_amp = np.zeros([nsamples, ntraces])
    array_amp[ twedge, np.arange(ntraces)] += Rp0
    array_amp[ bwedge, np.arange(ntraces)] += Rp1
            
    result = do_convolve(ntraces,f,0.001,array_amp,type='wedge')
    
    return result

def get_reflectivity(data, colourmap, theta=0, f=25, reflectivity_method='zoeppritz'):
    '''
    Create reflectivities from model.
    
    :param model: the physical model to use
    :param theta: angle of incidence
    :param f: the frequency for the wavelet
    :param reflectivity_method: the reflectivity algorithm to use
    '''

    model = []

    for row in range(data.shape[0]):
        model.append([])
        for col in range(data.shape[1]):
            model[row].append(colourmap[data[row,col]])
    
    # Transpose the model so we can work on columns (traces) not rows
    #model = map(list,zip(*model))
    
    # Search nd replace for dict items
    # Use the colourmap to put rocks in the array
    # Doesn't works because different types
    #for key, value in colourmap.iteritems():
    #    model[data==key] = value
         
    output = np.zeros( data.shape )

    for trace in range(len(model[0])):
        for sample in range(len(model) - 1):
            output[sample,trace] = reflectivity_method(model[sample][trace], model[sample+1][trace], theta)
            
    array_amp = output    
    
    traces = data.shape[0]
            
    result = do_convolve(traces,f,0.001,array_amp)
    
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