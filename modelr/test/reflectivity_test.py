import unittest
from bruges import reflection as avo
import numpy as np
from modelr.rock_properties import RockProperties
from modelr.reflectivity import rock_reflectivity, get_reflectivity, \
    do_convolve, get_boundaries
from bruges.filter import ricker

from svgwrite import rgb


class ReflectivityTest(unittest.TestCase):

    vp0 = 1500.0
    vs0 = 1200.0
    rho0 = 2000.0

    vp1 = 1800.0
    vs1 = 1400.0
    rho1 = 2200.0

    Rp0 = RockProperties(vp0, vs0, rho0)
    Rp1 = RockProperties(vp1, vs1, rho1)

    def test_wrapper(self):
        """
        Tests the reflectivity wrapper function
        """

        theta = 15.0

        ref_wrap = rock_reflectivity(self.Rp0, self.Rp1,
                                     theta=theta,
                                     method=avo.zoeppritz)

        ref = avo.zoeppritz(self.vp0, self.vs0, self.rho0,
                            self.vp1, self.vs1, self.rho1,
                            theta)

        self.assertEqual(ref, ref_wrap)

    def test_get_boundaries(self):

        data = np.zeros((100, 100, 3))

        data[:50, :, :] += [150, 100, 100]
        data[50:, :, :] += [100, 150, 100]

        boundaries = get_boundaries(data)

        # Check for the right number of interface indices
        self.assertEqual(boundaries.shape, (100, 2))
        for i in range(boundaries.shape[0]):
            self.assertEquals(boundaries[i, 0], 49)

    def test_get_reflectivity(self):

        cmap = {rgb(150, 100, 100): self.Rp0, rgb(100, 150, 100): self.Rp1}
        theta = 15.0
        data = np.zeros((100, 100, 3))

        data[:50, :, :] += [150, 100, 100]
        data[50:, :, :] += [100, 150, 100]

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

    
        self.assertTrue( np.allclose( truth, con ) )

if __name__ == '__main__':

    suite = \
      unittest.TestLoader().loadTestsFromTestCase(ReflectivityTest)
    unittest.TextTestRunner(verbosity=2).run(suite)















