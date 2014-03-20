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
                 vs_sig=0, rho_sig=0, units='si'):

        # Deal with Imperial units

        if units != 'si':
            vp  = vp  * 0.30480
            vs  = vs  * 0.30480
            rho = rho * 1000.0

            vp_sig  = vp_sig  * 0.30480
            vs_sig  = vs_sig  * 0.30480
            rho_sig = rho_sig * 1000.0


        # Deal with missing values

        # Simple Vp/Vs ratio
        if vs is None:
            vs = vp / 2.0
        else:
            vs = vs
            
        # Gardner equation
        if rho is None:
            rho = 1000 * 0.23 * (vp * 3.28084)**0.25
        else:
            rho = rho
            

        # Set properties

        self.vp = vp
        self.vs = vs
        self.rho = rho

        self.vp_sig = vp_sig
        self.vs_sig = vs_sig
        self.rho_sig = rho_sig
        
    def __repr__(self):
        return 'RockProperties(vp=%r, rho=%r, vs=%r)' % \
          (self.vp, self.rho, self.vs)
        

