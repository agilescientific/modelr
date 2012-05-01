'''

Module Containing wavelet functions.

Created on Apr 30, 2012

@author: sean
'''
import numpy as np

def ricker(points, a):
    """
    Also known as the "mexican hat wavelet",
    models the function:
    A ( 1 - x^2/a^2) exp(-t^2/a^2),
    where ``A = 2/sqrt(3a)pi^1/3``

    Parameters
    ----------
    a: scalar
        Width parameter of the wavelet.
    points: int, optional
        Number of points in `vector`. Default is ``10*a``
        Will be centered around 0.
    Returns
    -----------
    vector: 1-D ndarray
        array of length `points` in shape of ricker curve.
    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> points = 100
    >>> a = 4.0
    >>> vec2 = ricker(a,points)
    >>> print len(vec2)
    100
    >>> plt.plot(vec2)
    >>> plt.show()
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
    
    
    """
    
    pi2 = (np.pi ** 2.0)
    fsqr = f ** 2

    t = np.linspace(-.1, .1, points)
#    t = np.arange(0, points, 1.0)
    tsqr = t ** 2
    pft = pi2 * fsqr * tsqr
    
    A = (1 - (2 * pft)) * np.exp(-pft)
      
    return A

def klauder(points, fu, fl):
    """
    The autocorrelation of a linearly swept frequency-modulated sinuusoidal signal used in Vibroseis.
    It is zero-phase, and symmetrical about time t = 0 ms.
    Requires f_upper and f_lower, and a duration, which we can interpret from points.
    """
    
    T = points * 0.001
    t = np.linspace(-.1, .1, points)
    k = (fu + fl) / T
    f0 = (fu + fl) / 2.0
    i = (0 + 1j)
    A = np.real( np.sin(np.pi * k * t * (T - t))/(np.pi * k * t * np.exp(2.0 * np.pi * f0 * t * i)))

    return A

