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
from numpy import sin, cos, radians, arcsin


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
    
