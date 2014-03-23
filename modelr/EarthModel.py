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
        img = Image.open(StringIO(response.content))
        img.load()

        print earth_structure
        self.image = np.asarray(img, dtype="int32")
        self.depth = earth_structure["depth"]
        self.length = earth_structure["length"]

        self.units = earth_structure["units"]

        self.property_map = {}

        # Keep only a direct map for legacy. Input data has name
        # attribute we are going to ignore
        mapping = earth_structure["mapping"]
        for colour in mapping:
            self.property_map[colour] = mapping[colour]["property"]
        


    def time2depth(self, dz):
        
        if self.units == 'depth':
            raise ValueError

        vp_data = self.vp_data()
        dt = self.depth / self.shape[0]
        self.image = time_to_depth(data, vp_data, dt, dz)

    def depth2time(self, dt):

        if self.units == 'time':
            raise ValueError
        
        vp_data = self.vp_data()
        
        dz = self.depth / self.shape[0]
        self.image = depth_to_time(data, vp_data, dz, dt)
        
        
    def vp_data(self):

        vp_data = np.zeros(self.image.shape[0:2])
            
        for i in range(self.image.shape[0]):
            for j in range(self.image.shape[1]):
                value = self.image[i,j,:]
                rgb_string = rgb(value[0], value[1], value[2])
                vp_data[i,j] = self.property_map.get(rgb_string).vp

        return vp_data
    
    

    
        
