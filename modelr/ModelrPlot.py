from matplotlib import pyplot as plt

class ModelrPlot(object):

    def __init__(self, plot_json):

        self.cross_section = plot_json["cross_section"]
        self.trace = plot_json["trace"]
        self.centre_frequency = plot_json["center_frequency"]

        if twt:
            self.twt = plot_json["twt"]
            
        self.overlay = plot_json["overlay"]

    
        
    
