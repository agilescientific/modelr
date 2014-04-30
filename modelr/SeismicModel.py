'''
=========================
modelr.SeismicModel.py
=========================

Container for handling seismic models.
'''
from modelr.constants import WAVELETS, wavelet_duration,\
     REFLECTION_MODELS
import numpy as np
from modelr.web.urlargparse import SendHelp, ArgumentError, \
     URLArgumentParser

from agilegeo.avo import time_to_depth, depth_to_time

import h5py

class SeismicModel(object):
    '''
    Class to store earth models.
    '''
    
    def __init__(self, seismic_params, namespace):
        """
        Class for handling seismic models.

        :param seismic_params: A SeismicModel JSON dictionary.
        :param namespace: Name space of the modeling script
        """

                # Parse additional arguments that may be required by the
        # script
        
        add_arguments = namespace['add_arguments']
        short_description = namespace.get('short_description',
                                                  'No description')

        parser = URLArgumentParser(short_description)
        add_arguments(parser)
        try:
            args = parser.parse_params(seismic_params)
        except SendHelp as helper:
            raise SendHelp

        self.args = args
        self.script = namespace['run_script']

        self.wavelet_model = args.wavelet
        self.reflectivity_method = args.reflectivity_method

        self.f_res = 'octave' #args.f_res
        self.stack = 45 #args.stack
        
        self.n_sensors = 75 #args.sensor_spacing
        self.dt = 0.005 #args.dt
        self.start_f = 8 #args.f1
        self.end_f = 100 #args.f2

        self.theta1 = 0.0 #args.theta1
        self.theta2 = 45.0 #args.theta2


        
    def wavelets(self):

        f = self.wavelet_cf()

        wavelet = self.wavelet_model(wavelet_duration,
                                     self.dt, f)
        return wavelet

    def offset_angles(self):
            
        return np.linspace(self.theta1, self.theta2, self.stack)
    

    def wavelet_cf(self):
        # convenience
        f0 = self.start_f
        f1 = self.end_f

        if f0 == f1:
            return [f0]
        
        if self.f_res == "octave":
            f = np.logspace(max(np.log2(f0),np.log2(7)),
                            np.log2(f1),50,
                            endpoint=True,
                            base=2.0)
        if self.f_res == "linear":
            f = np.linspace(f0, f1, (f1-f0)/.5)

        return f

        
    def go(self,earth_model):

        self.seismic, self.reflectivity = \
          self.script(earth_model, self)

          

    def save(self, filename):


        with h5py.File(filename,'w') as f:
        
            seismic = f.create_dataset("seismic",
                                       data=self.seismic)
            reflectivity = f.create_dataset("reflectivity",
                                            data=self.reflectivity)
    


        
    

    
