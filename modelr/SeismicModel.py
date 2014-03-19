'''
=========================
modelr.SeismicModel.py
=========================

Container for handling seismic models.
'''
from modelr.constants import WAVELETS, wavelet_duration
import numpy as np

class SeismicModel(object):
    '''
    Class to store earth models.
    '''
    
    def __init__(self, seismic_params):
        """
        Class for handling seismic models.

        :param seismic_params: A SeismicModel JSON dictionary.
        """

        self.wavelet_model = \
          WAVELETS.get(seismic_params["wavelet_type"])
        self.reflectivity_model = \
          REFLECTION_MODELS.get(seismic_params["reflectivity"])

        self.f_res = seismic_params["f_res"]
        self.theta_res = seismic_params["theta_res"]
        self.sensor_spacing = seismic_params["sensor_spacing"] 
        self.dt = seismic_params["dt"]
        self.start_f = seismic_params["start_f"]
        self.end_f = seismic_params["end_f"]

        self.theta1 = seismic_params["theta1"]
        self.theta2 = seismic_params["theta2"]

        

    def generate_wavelets(self):

        # convenience
        f0 = self.start_f
        f1 = self.end_f
        
        if self.f_res == "octave"
            f = np.logspace(max(np.log2(f0),np.log2(7)),
                            np.log2(f1),300,
                            endpoint=True,
                            base=2.0)
        if self.f_res == "linear":
            f = np.linspace(f0, f1, (f1-f0)/.5)

        wavelet = self.wavelet_model(wavelet_duration,
                                     self.dt, f)

        if wavelet.ndim==1:
            wavelet = wavelet.flatten()

        return wavelet

    def offset_angles(self):

        return np.linspace(self.theta1, self.theta2, self.theta_res)
    


    def convolution_model(self):

        
        

