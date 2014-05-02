
from modelr.reflectivity import get_reflectivity, do_convolve
import os

class ForwardModel(object):

    def __init__(self, earth_model, seismic_model, plots):

        self.earth_model = earth_model

        
        self.seismic_model = seismic_model
        self.plots = plots

    def go(self):

        self.plots.go(self.seismic_model, self.earth_model)

        return self.plots.plot
          
          
                                                      
        
                                        
        


    
