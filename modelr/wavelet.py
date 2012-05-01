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

def klauder(points, f_lower, f_upper):
    """
    The autocorrelation of a linearly swept frequency-modulated sinuusoidal signal used in Vibroseis.
    It is zero-phase, and symmetrical about time t = 0 ms.
    Requires f_upper and f_lower, and a duration, which we can interpret from points.
    """
    
    T = points * 0.001
    t = np.linspace(-.1, .1, points)
    k = (f_lower + f_upper) / T
    f0 = (f_lower + f_upper) / 2.0
    i = (0 + 1j)
    A = np.real( np.sin(np.pi * k * t * (T - t))/(np.pi * k * t * np.exp(2.0 * np.pi * f0 * t * i)))

    return A

def ormsby(points, f1, f2, f3, f4):
    """
    The Ormsby wavelet requires four frequencies:
    f1 = low-cut frequency
    f2 = low-pass frequency
    f3 = high-pass frequency
    f4 = hi-cut frequency
    
    Together, the frequencies define a trapezoid shape in the spectrum.
    The Ormsby wavelet has several sidelobes, unlike Ricker wavelets
    which only have two, one either side. 
    """

    t = np.linspace(-.1, .1, points)
    
    def numerator(f,t):
        return np.sinc(np.pi * f * t)**2 * ((np.pi * f) ** 2)

    pf43 = np.pi * f4 - np.pi * f3
    pf21 = np.pi * f2 - np.pi * f1

    A = numerator(f4,t)/pf43 - numerator(f3,t)/pf43 - numerator(f2,t)/pf21 + numerator(f1,t)/pf21

    return A

