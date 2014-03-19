from matplotlib import pyplot as plt

class ModelrPlot(object):

    def __init__(self, plot_json):

        self.cross_section = plot_json["cross_section"]
        self.trace = plot_json["trace"]
        self.centre_frequency = plot_json["center_frequency"]

        if twt:
            self.twt = plot_json["twt"]
            
        self.overlay = plot_json["overlay"]


    def plot(self, seismic_data, seismic_model, earth_image,
             reflectivity)

        if self.cross_section == 'spatial':
            data = seismic[:,:,0,:]
        elif self.cross_section == 'angle':
            data = 
        
    
