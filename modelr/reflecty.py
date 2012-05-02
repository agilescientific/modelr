#!/usr/bin/env python
#
#   Python application for calculating angle-dependent p-wave reflectivity
#   using Zoeppritz equations & various approximations.
#
#   Originally written to give insight into limitations of the Zoeppritz
#   approximations and to get more familiar with GUI programming using wxPython
#   and Matplotlib.
#
#   Requires:   Python (2.6 or 2.7)
#               wxPython
#               Numpy & Matplotlib
#
#       Written by: Wes Hamlyn
#       Modified by: Sean Ross-Ross
#       Last Mod:   May 1, 2012
#
#   Use for whatever you like but at your own risk...
#

import numpy as np
from numpy import log, tan, sin, cos, arcsin, arccosh, radians, degrees


def zoeppritz(vp1, vs1, rho1, vp0, vs0, rho0, theta1):
    '''
    Documentation goes here. 
    '''
        # Get the input data from the text controls tc*
    p = sin(radians(theta1)) / vp1 # ray parameter
    
    # Calculate reflection & transmission angles for Zoeppritz
    theta1 = radians(theta1)   # Convert theta1 to radians
    theta2 = arcsin(p * vp0);      # Trans. angle of P-wave
    phi1 = arcsin(p * vs1);      # Refl. angle of converted S-wave
    phi2 = arcsin(p * vs0);      # Trans. angle of converted S-wave
                
    # Matrix form of Zoeppritz Equations... M & N are matricies
    M = np.array([ \
        [-sin(theta1), -cos(phi1), sin(theta2), cos(phi2)], \
        [cos(theta1), -sin(phi1), cos(theta2), -sin(phi2)], \
        [2 * rho1 * vs1 * sin(phi1) * cos(theta1), rho1 * vs1 * (1 - 2 * sin(phi1) ** 2), \
            2 * rho0 * vs0 * sin(phi2) * cos(theta2), \
            rho0 * vs0 * (1 - 2 * sin(phi2) ** 2)], \
        [-rho1 * vp1 * (1 - 2 * sin(phi1) ** 2), rho1 * vs1 * sin(2 * phi1), \
            rho0 * vp0 * (1 - 2 * sin(phi2) ** 2), -rho0 * vs0 * sin(2 * phi2)]
        ], dtype='float')
    
    N = np.array([ \
        [sin(theta1), cos(phi1), -sin(theta2), -cos(phi2)], \
        [cos(theta1), -sin(phi1), cos(theta2), -sin(phi2)], \
        [2 * rho1 * vs1 * sin(phi1) * cos(theta1), rho1 * vs1 * (1 - 2 * sin(phi1) ** 2), \
            2 * rho0 * vs0 * sin(phi2) * cos(theta2), rho0 * vs0 * (1 - 2 * sin(phi2) ** 2)], \
        [rho1 * vp1 * (1 - 2 * sin(phi1) ** 2), -rho1 * vs1 * sin(2 * phi1), \
            - rho0 * vp0 * (1 - 2 * sin(phi2) ** 2), rho0 * vs0 * sin(2 * phi2)]\
        ], dtype='float')
    
    # This is the important step, calculating coefficients for all modes
    # and rays result is a 4x4 matrix, we want the R[0][0] element for
    # Rpp reflectivity only
    
    if M.ndim == 3:
        zoep = np.zeros([M.shape[-1]])
        for i in range(M.shape[-1]): 
            Mi = M[..., i]
            Ni = N[..., i]
            dt = np.dot(np.linalg.inv(Mi), Ni)
            zoep[i] = dt[0][0]
    else:
        dt = np.dot(np.linalg.inv(M), N)
        zoep = dt[0][0]
    
    return zoep

def akirichards(vp2, vs2, rho2, vp1, vs1, rho1, theta1):
    """
    Doumentation goes here.
    """

    # We are not using this for anything, but will
    # critical_angle = arcsin(vp1/vp2)
    
    # Do we need to ensure that we get floats out before computing sines?
    vp1 = float(vp1)    

    theta2 = degrees(arcsin(vp2/vp1*sin(radians(theta1))))

    # Compute the various parameters
    drho = rho2-rho1
    dvp = vp2-vp1
    dvs = vs2-vs1
    theta = (theta1+theta2)/2.0
    rho = (rho1+rho2)/2.0
    vp = (vp1+vp2)/2.0
    vs = (vs1+vs2)/2.0

    # Compute the three terms
    term1 = 0.5*(dvp/vp + drho/rho)
    term2 = (0.5*dvp/vp-2*(vs/vp)**2*(drho/rho+2*dvs/vs))*sin(radians(theta))**2
    term3 = 0.5*dvp/vp*(tan(radians(theta))**2 - sin(radians(theta))**2)
    
    return (term1 + term2 + term3)

def shuey(vp2, vs2, rho2, vp1, vs1, rho1, theta1):
    """
    Compute Shuey approximation.
    Could use refactoring.
    """

    # Compute some parameters
    pr1 = ( (vp1/vs1)**2 - 2 )/( 2*((vp1/vs1)**2 - 1) )
    pr2 = ( (vp2/vs2)**2 - 2 )/( 2*((vp2/vs2)**2 - 1) )
    dpr = pr2 - pr1
    pr = (pr1 + pr2) / 2.0
    drho = rho2-rho1
    dvp = vp2-vp1
    dvs = vs2-vs1
    rho = (rho1+rho2)/2.0
    vp = (vp1+vp2)/2.0
    vs = (vs1+vs2)/2.0
    f = (dvp/vp) / (dvp/vp + drho/rho)
    e = f - 2.0 * (1.0+f) * (1.0-2.0*pr) / (1.0-pr)

    # Compute two-term reflectivity
    
    r0 = 0.5 * (dvp/vp + drho/rho)
    g = (e * r0 + dpr/((1.0-pr)**2))
    # We are not computing the third term here
    # but if we were, here it is
    # c = 0.5 * dvp/vp

    return r0 + g * sin(radians(theta1))**2

#def bortfeld(vp2, vs2, rho2, vp1, vs1, rho1, theta1):
#    """
#    Documentation for the Bortfeld approximation.
#    This bit doesn't work, at least not for wide angles.
#    """
#    
#    # Bortfeld only needs one extra parameter
#    theta2 = degrees(arcsin(vp2/vp1*sin(radians(theta1))))
#
#    term1_bf = 0.5 * log( (vp2*rho2*cos(radians(theta1)))/(vp1*rho1*cos(radians(theta2))) )
#    term2_bf = (sin(radians(theta1))/vp1)**2 * (vs1**2-vs2**2) * (2+log(rho2/rho1)/log(vs2/vs1))
#
#    return term1_bf + term2_bf
#
