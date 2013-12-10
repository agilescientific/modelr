import unittest
import modelr.modelbuilder as mb
import numpy as np
from matplotlib import pyplot as plt

class ModelBuilderTest( unittest.TestCase ):

    def test_body( self ):

        samp_pad = 150
        margin = 0
        t1 = (50,150)
        t2 = (150,250)
        ntraces = 300
        l1 = (150,100,100)
        l2 = (100,150,100)
        l3 = (100,100,150)
        layers= (l1,l2,l3)
        svg_file = mb.body_svg( samp_pad, margin,
                                t1,t2,
                                300, layers )

        png_file = mb.svg2png( svg_file, layers)

        array = mb.png2array( png_file )

        # Test some values from layer 1
        self.assertTrue( np.array_equal( array[100,20,:], l1 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[0]-1,
                                               0,:], l1 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[0]-1,
                                               -1,:], l1 ) )
        
        
        # Test some from the wedge
        self.assertTrue( np.array_equal( array[225,20,:], l2 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[0],
                                               0,:], l2 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[1]-1,
                                               0,:], l2 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[1]-1,
                                               -1,:], l2 ) )

        # Test some from the bottom
        self.assertTrue( np.array_equal( array[400,20,:], l3 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[0],
                                               0,:], l3 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t1[1],
                                               0,:], l3 ) )
        self.assertTrue( np.array_equal( array[samp_pad + t2[1],
                                               -1,:], l3 ) )
        
        
    """def test_channel( self ):

        pad = 150
        thickness = 50
        traces = 300
        l1 = (150,100,100)
        l2 = (100,150,100)
        l3 = (100,100,150)
        layers= (l1,l2,l3)

        svg_file = mb.channel_svg( pad, thickness,
                                   traces, layers )
        png_file = mb.svg2png( svg_file )
        array = mb.png2array( png_file )

        print( array[ pad-1 , 0, : ] )
        # Upper
        self.assertTrue( np.array_equal( array[ pad-1 , 0, : ],
                                        l1 ) )
        # Upper and lower interface
        self.assertTrue(np.array_equal( array[ pad , 0, : ],
                                         l3 ) )
        # Upper and Body
        self.assertTrue(np.array_equal( array[ pad+1 , 150,: ],
                                         l2 ) )
        
    def test_web2array( self ):
        wparray =  \
          mb.web2array('http://www.subsurfwiki.org' +
                    '/mediawiki/images/8/84/Modelr_test_ellipse.svg')
    """
if __name__ == '__main__':

    suite = \
      unittest.TestLoader().loadTestsFromTestCase(ModelBuilderTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

