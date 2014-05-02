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

from PIL import Image
from StringIO import StringIO
from svgwrite import rgb

from modelr.web.urlargparse import SendHelp, ArgumentError, \
     URLArgumentParser, rock_properties_type
import h5py

import os

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
        if earth_structure.get('update', None):
            response = requests.get(earth_structure["image"])

            if os.path.exists(self.reflect_file):
                os.remove(self.reflect_file)

            image = Image.open(StringIO(response.content)).convert("RGB")
            image.load()
            self.image = np.asarray(image, dtype="int32")

            self.units = args.units
            self.depth = args.depth
            self.reflectivity_method = args.reflectivity_method

            self.property_map = {}

            # Keep only a direct map for legacy. Input data has name
            # attribute we are going to ignore
            mapping = earth_structure["mapping"]
    
            for colour in mapping:
                rock = mapping[colour]["property"]

                self.property_map[colour] = rock_properties_type(rock)
    

    def time2depth(self, dz):
        
        if self.units == 'depth':
            raise ValueError

        vp_data = self.vp_data()
        dt = self.depth / vp_data[0]

        data = np.zeros

        # This could be sped up if need be
        data = np.asarray([time_to_depth(self.get_data(), vp_data,
                                         dt, dz)
                           for i in range(data.shape[-1])])


    def depth2time(self, dt):

        if self.units == 'time':
            raise ValueError
        
        vp_data = self.vp_data()
        
        data = self.get_data()
        
        dz = self.depth / data.shape[0]
        
        self.image =\
          np.asarray([depth_to_time(data[:,:,i],vp_data,dz, dt)
                    for i in range(data.shape[-1])]).transpose(1,2,0)
        
        
    def vp_data(self):

        data = self.get_data()
    
        vp_data = np.zeros(data.shape[0:2])

        # TODO this could likely be done without nested loops
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                value = data[i,j,:]
                rgb_string = rgb(value[0], value[1], value[2])
                vp_data[i,j] = self.property_map.get(rgb_string).vp

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

        step = int(self.image.shape[1] / samples)
        
        return self.image[:,
                          np.arange(0,self.image.shape[1],step),
                          :]

        
        
        
