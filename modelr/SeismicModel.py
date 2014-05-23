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

from agilegeo.wavelet import rotate_phase

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

        #self.noise = args.noise / 1000.0
        self.wavelet_model = args.wavelet

        self.f_res = 'octave' #args.f_res
        self.stack = 50 #args.stack

        self.phase = args.phase * np.pi / 180.0
        self.n_sensors = 350 #args.sensor_spacing
        self.dt = 0.002 #args.dt

        self.f = args.f
        
        self.start_f = 8.0 #args.f1
        self.end_f = 100.0 #args.f2


        self.theta1 = 0.0 #args.theta1
        self.theta2 = 45.0 #args.theta2


        
    def wavelets(self):

        f = self.wavelet_cf()

        if ((self.wavelet_model == WAVELETS['ormsby']) and
            (np.size(f) > 1)):
            wavelet = np.zeros((wavelet_duration/self.dt,np.size(f)))
            for ind, freq in enumerate(f):
                wavelet[:,ind] = self.wavelet_model(wavelet_duration,
                                                    self.dt, freq)
        else:   
            wavelet = self.wavelet_model(wavelet_duration,
                                         self.dt, f)

        return rotate_phase(wavelet, self.phase)

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

        return f[self.f]

        
    def go(self,earth_model, theta=None, traces=None,
           wavelet=None):

        self.seismic = self.script(earth_model, self,
                                   theta=theta,
                                   traces=traces)

    


        
    

    
