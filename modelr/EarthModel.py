'''
=========================
modelr.EarthModel.py
=========================

Container for handling earth models.
'''

from agilegeo.avo import time_to_depth, depth_to_time
import urllib
import requests

import numpy as np

from PIL import Image
from StringIO import StringIO
from svgwrite import rgb

from modelr.web.urlargparse import rock_properties_type

class EarthModel(object):
    '''
    Class to store earth models.
    '''
    
    def __init__(self,earth_structure):
        """
        Class for handling earth models.

        :param earth_structure: An EarthStructure JSON dictionary. 
        """

        # Load the image data
        response = requests.get(earth_structure["image"])

        image = Image.open(StringIO(response.content)).convert("RGB")
        image.load()
        self.image = np.asarray(image, dtype="int32")
        
        self.depth = float(earth_structure["depth"])
        self.length = float(earth_structure["length"])

        self.units = earth_structure["units"]

        self.property_map = {}

        # Keep only a direct map for legacy. Input data has name
        # attribute we are going to ignore
        mapping = earth_structure["mapping"]
    
        for colour in mapping:
            rock = mapping[colour]["property"]
            
            self.property_map[colour] = rock_properties_type(rock)
        

        print self.depth, self.length, self.units
        
    def time2depth(self, dz):
        
        if self.units == 'depth':
            raise ValueError

        vp_data = self.vp_data()
        dt = self.depth / vp_data[0]

        data = np.zeros
        data = np.asarray([time_to_depth(self.get_data(), vp_data,
                                         dt, dz)
                           for i in range(data.shape[-1])])


    def depth2time(self, dt):

        if self.units == 'time':
            raise ValueError
        
        vp_data = self.vp_data()
        
        data = self.get_data()
        
        dz = self.depth / data.shape[0]
        
        self.image = np.asarray([depth_to_time(data[:,:,i],vp_data,
                                               dz, dt)
                      for i in range(data.shape[-1])]).transpose(1,2,0)
        
        
    def vp_data(self):

        data = self.get_data()
    
        vp_data = np.zeros(data.shape[0:2])
            
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                value = data[i,j,:]
                rgb_string = rgb(value[0], value[1], value[2])
                vp_data[i,j] = self.property_map.get(rgb_string).vp

        return vp_data



    
    def get_data(self, samples=None):

        if samples is None:
            return self.image

        res = self.image.shape[1] / float(self.length)

        pixel_samples = (samples * res)
        pixel_samples = \
          pixel_samples[pixel_samples < self.image.shape[1]]

        return self.image[:, pixel_samples.astype(int),:]

        
        
        
