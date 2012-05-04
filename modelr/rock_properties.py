'''
================================================================
modelr.rock_properties -- TODO short docstring here
================================================================

TODO: long doc here 
'''

from modelr.reflecty import zoeppritz, akirichards_alt, akirichards, fatti,\
    shuey3, shuey2, bortfeld2, bortfeld3
    
class RockProperties(object):
    '''
    Class to store rock properties.
    
    :param vp: pressure wave coef
    :param vs: shear wave coef
    :param rho: TODO
    
    '''
    
    def __init__(self, vp, rho, vs=None):
        self.vp = vp
        if vs is None:
            self.vs = vp / 2.0
        else:
            self.vs = vs
        self.rho = rho
        
    def __repr__(self):
        return 'RockProperties(vp=%r, rho=%r, vs=%r)' % (self.vp, self.rho, self.vs)
        
def zoeppritz(Rp0, Rp1, theta1):
    '''
    Wrapper around long zoeppritz funcion.
    
    :param Rp0:
    :param Rp1:
    :param theta1:
     
    '''
    return zoeppritz(Rp0.vp, Rp0.vs, Rp0.rho,
                     Rp1.vp, Rp1.vs, Rp1.rho,
                               theta1)    



def akirichards(Rp0, Rp1, theta1):
    akirichards(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def akirichards_alt(Rp0, Rp1, theta1):
    akirichards_alt(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def fatti(Rp0, Rp1, theta1):
    fatti(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def shuey2(Rp0, Rp1, theta1):
    shuey2(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def shuey3(Rp0, Rp1, theta1):
    shuey3(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)

def bortfeld2(Rp0, Rp1, theta1):
    bortfeld2(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)
    
def bortfeld3(Rp0, Rp1, theta1):
    bortfeld3(Rp0.vp, Rp0.vs, Rp0.rho, Rp1.vp, Rp1.vs, Rp1.rho, theta1)
    
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
