
from modelr.reflectivity import get_reflectivity, do_convolve
import os

class ForwardModel(object):

    def __init__(self, earth_model, seismic_model, plots):

        self.earth_model = earth_model
        self.seismic_model = seismic_model
        self.plots = plots

    def go(self):

        if not os.path.exists('testfile.hdf5'):
            
            self.seismic_model.go(self.earth_model)
            self.seismic_model.save('testfile.hdf5')

        self.plots.go(self.earth_model, self.seismic_model)

        return self.plots.plot
          
          
                                                      
        
                                        
        


    
