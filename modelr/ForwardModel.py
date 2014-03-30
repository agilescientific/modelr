
from modelr.reflectivity import get_reflectivity, do_convolve

class ForwardModel(object):

    def __init__(self, earth_model, seismic_model, plots):

        self.earth_model = earth_model
        self.seismic_model = seismic_model
        self.plots = plots

    def go(self):

        # Do time to depth conversions
        self.seismic_model.go(self.earth_model)

        ## TODO calculate metadata

        # TODO make plots a loop

        self.plots.go(self.earth_model, self.seismic_model)

        return self.plots.plot
          
          
                                                      
        
                                        
        


    
