# -*- coding: utf-8 -*-
'''
===================
ForwardModel.py
===================

Provide the forward model object.

@author: Ben Bougher
'''
import matplotlib
matplotlib.use('Agg')
from modelr.reflectivity import get_reflectivity, do_convolve
import os
import numpy as np

import json

class ForwardModel(object):

    def __init__(self, earth_model, seismic_model, plots):

        self.earth_model = earth_model
        
        self.seismic_model = seismic_model
        self.plots = plots

    def go(self):

        self.plots.go(self.seismic_model, self.earth_model)

        metadata = {}

        f = self.seismic_model.wavelet_cf()

        if np.ndim(f) == 0:
            f = [f]
        
        metadata["f"] = tuple(f)
        metadata["time"] = \
          tuple(np.arange(self.seismic_model.seismic.shape[0]) *
                self.seismic_model.dt*1000)

        metadata["trace"] = \
          tuple(range(1,self.seismic_model.n_sensors +1))

        metadata["gain"] = tuple(np.linspace(0.0,2.0, 1000))

        metadata["snr"] = tuple(np.linspace(-50.0, 50.0, 1000))

        metadata["moduli"] = {}
        for rock in self.earth_model.get_rocks():
            if not rock.name in metadata["moduli"]:
                metadata["moduli"][rock.name] = rock.get_moduli()

        # --------------------------
        # Resuming normal service
        return self.plots.plot, metadata

    
