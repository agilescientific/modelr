import unittest
import modelr.modelbuilder as mb
import numpy as np

class ModelBuilderTest( unittest.TestCase ):

    def test_body( self ):

        samp_pad = 100
        margin = 0
        t1 = (50,150)
        t2 = (150,250)
        ntraces = 300
        l1 = (255,0,0)
        l2 = (0,255,0)
        l3 = (0,0,255)
        layers= (l1,l2,l3)
        svg_file = mb.body_svg( samp_pad, margin,
                                t1,t2,
                                300, layers )

        png_file = mb.svg2png( svg_file, colours = 3)

        array = mb.png2array( png_file )

        # Test some values from layer 1
        self.assertTrue( np.array_equal( array[100,20,:], l1 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[0]-1,
                                               0,:], l1 ) )
        
        self.assertTrue( np.array_equal( array[samp_pad + t2[0]-1,
                                               -1,:], l1 ) )
        

        # Test some from the wedge
        self.assertTrue( np.array_equal( array[200,20,:], l2 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[0],
                                               0,:], l2 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[1]-1,
                                               0,:], l2 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[1]-1,
                                               -1,:], l2 ) )

        # Test some from the bottom
        self.assertTrue( np.array_equal( array[300,20,:], l3 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[0],
                                               0,:], l3 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[1],
                                               0,:], l3 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[1],
                                               -1,:], l3 ) )
        
        
        
if __name__ == '__main__':

    suite = \
      unittest.TestLoader().loadTestsFromTestCase(ModelBuilderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

