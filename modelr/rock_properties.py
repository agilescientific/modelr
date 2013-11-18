'''
================================================================
modelr.rock_properties -- TODO short docstring here
================================================================

TODO: long doc here 
'''

from agilegeo import avo as reflection
    
class RockProperties(object):
    '''
    Class to store rock properties.
    
    :param vp: pressure wave velocity
    :param vs: shear wave velocity
    :param rho: bulk density
    
    '''
    
    def __init__(self, vp, vs=None, rho=None, vp_sig=0, vs_sig=0, rho_sig=0):
                 
        self.vp = vp
        
        # This needs to be exposed to the user
        # Simple Vp/Vs ratio
        if vs is None:
            self.vs = vp / 2.0
        else:
            self.vs = vs
            
        # This needs to be exposed to the user
        # Gardner equation
        if rho is None:
            self.rho = 1000 * 0.23 * (vp * 3.28084)**0.25
        else:
            self.rho = rho
            
        self.vp_sig = vp_sig
        self.vs_sig = vs_sig
        self.rho_sig = rho_sig
        
    def __repr__(self):
        return 'RockProperties(vp=%r, rho=%r, vs=%r)' % \
          (self.vp, self.rho, self.vs)
        
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
          'bortfeld2': bortfeld2,
          'bortfeld3': bortfeld3,
          }

# No longer in use?
#FUNCTIONS = {
#             'zoeppritz': reflection.zoeppritz,
#             'akirichards': reflection.akirichards,
#             'akirichards_alt': reflection.akirichards_alt,
#             'fatti': reflection.fatti,
#             'shuey2': reflection.shuey2,
#             'shuey3': reflection.shuey3
#             'bortfeld2': bortfeld2,
#             'bortfeld3': bortfeld3,
#             }
