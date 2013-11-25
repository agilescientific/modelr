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
