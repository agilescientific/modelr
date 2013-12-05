import unittest
from agilegeo import avo
import numpy as np
from modelr.rock_properties import RockProperties
from modelr.reflectivity import rock_reflectivity, get_reflectivity, \
     do_convolve
from agilegeo.wavelet import ricker

from matplotlib import pyplot as plt

class ReflectivityTest( unittest.TestCase ):

    vp0 = 1500.0
    vs0 = 1200.0
    rho0 = 2000.0

    vp1 = 1800.0
    vs1 = 1400.0
    rho1 = 2200.0
        
    Rp0 = RockProperties( vp0, vs0, rho0 )
    Rp1 = RockProperties( vp1, vs1, rho1 )

    def test_wrapper( self ):
        """
        Tests the reflectivity wrapper function
        """
        
        theta = 15.0

        ref_wrap = rock_reflectivity( self.Rp0, self.Rp1,
                                      theta=theta,
                                      method=avo.zoeppritz )

        ref = avo.zoeppritz( self.vp0,self.vs0,self.rho0,
                             self.vp1, self.vs1, self.rho1,
                             theta )

        
        self.assertEqual( ref, ref_wrap )

    
    def test_get_reflectivity( self ):

        cmap = {1:self.Rp0, 2:self.Rp1}
        theta = 15.0
        data = np.zeros( (100,100 ) )

        data[:50,:] = 1
        data[50:,:] = 2

        reflectivity = \
          get_reflectivity( data, cmap, theta,
                            reflectivity_method=avo.zoeppritz )

        truth = avo.zoeppritz( self.vp0, self.vs0, self.rho0,
                               self.vp1, self.vs1, self.rho1,
                               theta )

        test = np.zeros( (100,100,1) )
        test[49,:,0] = truth

        self.assertTrue( np.array_equal( test, reflectivity ) )


    def test_do_convolve( self ):

        # Make a spike dataset [samp, trace, theta]
        data = np.zeros( (1000,100,10) )
        data[500,50,:] = 1.0

        dt = 0.001
        duration = .2
        f = (20,40,60)
        
        wavelets = ricker( duration, dt, f )
        
        con = do_convolve( wavelets, data )


        truth = np.zeros( (1000,100,10,3) )

        for i in range(10):
            truth[:wavelets.shape[0], 50, i, :] += wavelets
        
                 
        truth = np.roll( truth, 401, axis=0 )

        """fig = plt.figure()
        plt.plot( truth[:, 50, 0,0] )
        plt.plot( con[:, 50, 0,0])
        plt.show()"""
        self.assertTrue( np.allclose( truth, con ) )
     
        
        
        
        
        
        
if __name__ == '__main__':

    suite = \
      unittest.TestLoader().loadTestsFromTestCase(ReflectivityTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
