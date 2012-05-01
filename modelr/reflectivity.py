'''
Created on May 1, 2012

@author: sean
'''
import numpy as np
from modelr.rock_properties import zoeppritz
from modelr.wavelet import ricker_freq

def create_wedge(ntraces, pad, max_thickness, prop0, prop1, theta, f):
    
    scale = 10
    nsamples = (2 * pad + max_thickness) * scale
      
    array_amp = np.zeros([nsamples, ntraces])
    fwedge = np.floor(np.linspace(pad * scale, (pad + max_thickness) * scale, ntraces, endpoint=False))
    wedge = np.array(fwedge, dtype=int)
    
     
    Rp0 = zoeppritz(prop0, prop1, theta)
    Rp1 = zoeppritz(prop1, prop0, theta)
    
    array_amp[pad * scale, :] += Rp0
    array_amp[wedge, np.arange(ntraces)] += Rp1
    
    r = ricker_freq(100 * scale, f)
    
    warray_amp = np.zeros([max(array_amp.shape[0], r.shape[0]), array_amp.shape[1]])
    
    for i in range(ntraces):
        warray_amp[:, i] = np.convolve(array_amp[:, i], r, mode='same')
        
    return np.array(warray_amp[::scale, :])

