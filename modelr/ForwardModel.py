
from modelr.reflectivity import get_reflectivity, do_convolve
import os
import numpy as np

class ForwardModel(object):

    def __init__(self, earth_model, seismic_model, plots):

        self.earth_model = earth_model

        
        self.seismic_model = seismic_model
        self.plots = plots

    def go(self):

        self.plots.go(self.seismic_model, self.earth_model)

        metadata = {}
        
        metadata["f"] = tuple(self.seismic_model.wavelet_cf())
        metadata["time"] = \
          tuple(np.arange(self.seismic_model.seismic.shape[0]) *
                self.seismic_model.dt*100)
        
        return self.plots.plot, metadata
          
          
                                                      
        
                                        
        


    