'''
=========================
modelr.rock_properties
=========================

Container for physical rock properties
'''
    
class RockProperties(object):
    '''
    Class to store rock properties.
    
    :param vp: pressure wave velocity
    :param vs: shear wave velocity
    :param rho: bulk density
    
    '''
    
    def __init__(self, vp, vs=None, rho=None, vp_sig=0,
                 vs_sig=0, rho_sig=0):
                 
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
        

