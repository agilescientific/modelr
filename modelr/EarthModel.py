'''
=========================
modelr.EarthModel.py
=========================

Container for handling earth models.
'''

from agilegeo.avo import time_to_depth, depth_to_time, zoeppritz
import urllib
import requests

from modelr.reflectivity import get_reflectivity

import numpy as np
from scipy.interpolate import interp1d

from PIL import Image
from StringIO import StringIO

from modelr.web.urlargparse import SendHelp, ArgumentError, \
     URLArgumentParser, rock_properties_type
import h5py

import os

from scipy.interpolate import interp1d
class EarthModel(object):
    '''
    Class to store earth models.
    '''
    
    def __init__(self,earth_structure, namespace):
        """
        Class for handling earth models.

        :param earth_structure: An EarthStructure JSON dictionary. 
        """

        add_arguments = namespace['add_arguments']
        short_description = namespace.get('short_description',
                                          'No description')

        parser = URLArgumentParser(short_description)
        add_arguments(parser)
        try:
            args = parser.parse_params(earth_structure["arguments"])
        except SendHelp as helper:
            raise SendHelp
        
        self.reflect_file = str(earth_structure["datafile"])
        
        # Load the image data
        if earth_structure.get('update_model', None):
            response = requests.get(earth_structure["image"])

            if os.path.exists(self.reflect_file):
                os.remove(self.reflect_file)

            image = \
              Image.open(StringIO(response.content)).convert("RGB")
            image.load()
            self.image = np.asarray(image, dtype="int32")

            self.units = args.units
            self.depth = args.depth
            self.reflectivity_method = args.reflectivity_method

            self.property_map = {}

            # Keep only a direct map for legacy. Input data has name
            # attribute we are going to ignore
            mapping = earth_structure["mapping"]

            # Make a lookup table for vp. This is terribly
            # inefficient for memory, but quicker than looping
            # dictionaries. There is for sure a better way
            self.vp_lookup = np.zeros((256,256,256))
            for colour in mapping:
                rock = \
                  rock_properties_type(mapping[colour]["property"])

                rgb = colour.split('(')[1].split(')')[0].split(',')
                self.vp_lookup[int(rgb[0]), int(rgb[1]),
                               int(rgb[2])] = rock.vp
                                             
                self.property_map[colour] = rock
    

    def time2depth(self, dz):
        
        if self.units == 'depth':
            raise ValueError

        vp_data = self.vp_data()
        dt = self.depth / vp_data[0]

        # This could be sped up if need be
        data = np.asarray([time_to_depth(self.get_data(), vp_data,
                                         dt, dz)
                           for i in range(data.shape[-1])])


    def resample(self, dt):

        depth = self.depth / 1000.0
        res = depth / self.image.shape[0]

        model_time = np.arange(0, depth, res)
        new_time = np.arange(0, depth, dt)
        

        f = interp1d(model_time, self.image, kind='nearest',
                     axis=0, bounds_error=False,
                     fill_value=-1)
        self.image = f(new_time)

        
        
    def depth2time(self, dt, samples=None):

        if self.units == 'time':
            raise ValueError
        
        vp_data = self.vp_data(samples=samples)
        
        data = self.get_data(samples=samples)

        

        indices = \
          np.array([np.arange(vp_data.shape[0]) for \
                    i in range(vp_data.shape[1])]).transpose()

        
                            
        dz = self.depth / data.shape[0]

        time_index = depth_to_time(indices, vp_data,
                                   dz, dt).astype(int)

        self.image = \
          np.asarray([data[time_index[:,i],i,:] for \
                     i in range(data.shape[1])]).transpose(1,0,2)

        
    def vp_data(self, samples=None):

        data = self.get_data(samples=samples).astype(int)   
        vp_data = self.vp_lookup[data[:,:,0],
                                 data[:,:,1],
                                 data[:,:,2]]
        return vp_data



    def update_reflectivity(self, offset_angles,
                            samples=None):

        reflectivity = \
          get_reflectivity(data=self.get_data(samples=samples),
                           colourmap=self.property_map,
                           theta=offset_angles,
                           reflectivity_method=self.reflectivity_method)

        with h5py.File(self.reflect_file,'w') as f:
            f.create_dataset("reflectivity",
                             data=reflectivity)
        

    def reflectivity(self, theta=None):

        try:
            with h5py.File(self.reflect_file) as f:
                data = f["reflectivity"].value
                if theta:
                    data = data[:,:,[theta]]
                    

        except:
            data = None

        return data

    
    def get_data(self, samples=None):

        if samples is None:
            return self.image

        step = self.image.shape[1] / float(samples)
        # Check for interpolation
        if step % int(step):
            interp = interp1d(np.arange(self.image.shape[1]),
                              self.image,kind="nearest", axis=1,
                              )
            data = interp(np.linspace(0,self.image.shape[1]-1,samples))
            return data
        else:
            return self.image[:,
                              np.arange(0,self.image.shape[1],
                                        int(step)),
                              :]

        
        
        
