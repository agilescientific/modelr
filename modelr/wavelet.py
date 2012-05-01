'''
==============================================================
modelr.wavelet --- Module Containing wavelet functions.
==============================================================

TODO: long doc here
'''
import numpy as np

def ricker(points, a):
    """
    Also known as the "mexican hat wavelet",
    models the function:
    """

    A = 2 / (np.sqrt(3 * a) * (np.pi ** 0.25))
    wsq = a ** 2
    vec = np.arange(0, points) - (points - 1.0) / 2
    tsq = vec ** 2
    mod = (1 - tsq / wsq)
    gauss = np.exp(-tsq / (2 * wsq))
    total = A * mod * gauss
    return total

def ricker_freq(points, f):
    """
    Also known as the "mexican hat wavelet",
    models the function:
    
    A = (1-2 \pi^2 f^2 t^2) e^{-\pi^2 f^2 t^2}
    
    The amplitude ''A'' of the [[Ricker wavelet]] with peak frequency ''f'' at time ''t'' is computed like so:
    
    :params points: adsf
    :params f: asdf 
    
    :returns: adf
    
    """
    
    pi2 = (np.pi ** 2.0)
    fsqr = f ** 2

    t = np.linspace(-.1, .1, points)
#    t = np.arange(0, points, 1.0)
    tsqr = t ** 2
    pft = pi2 * fsqr * tsqr
    
    A = (1 - (2 * pft)) * np.exp(-pft)
      
    return A
