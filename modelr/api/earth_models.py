from modelrAPI import modelrAPI, Rock
from modelr.reflectivity import reflectivity_array
from PIL import Image
import numpy as np
from numpy.random import randn
import requests
from scipy.interpolate import interp1d
import h5py
from StringIO import StringIO
import md5
import json

from bruges.transform import depth_to_time


class ImageModel(modelrAPI):

    handler = 'earth_model'

    @classmethod
    def fill_mapping(cls, image, mapping):

        # Change from rock keys to rock objects in the mapping
        new_map = {colour: Rock.from_json(rock) for
                   colour, rock in mapping.iteritems()}

        return new_map
    
    def get_rocks(self):
        return self.map.values()
    
    def __init__(self, image, mapping,
                 zrange=1000, xrange=1000,
                 units="SI",
                 domain='depth',
                 theta=np.linspace(0, 45, 15),
                 resample=None):

        self.theta = theta
        self.units = units
        self.zrange = zrange
        self.domain = domain
        
        self.xrange = xrange

        # Change the mapping from RGB to index
        image = Image.open(image)
        if resample is not None:
            image = image.resize(resample, Image.NEAREST)
        
        index_mapping = {}
        for colour, rock in mapping.iteritems():
            rgb = np.array([[colour.split('(')[1].split(')')[0]
                             .split(',')]], 'uint8')
            
            index = np.asarray(Image.fromarray(rgb)
                               .quantize(palette=image)).flatten()[0]
            
            index_mapping[index] = rock

        self.map = index_mapping
        self.image = np.asarray(image.convert("P"))

        self.dz = self.zrange / float(self.image.shape[0])
        self.dx = self.xrange / float(self.image.shape[1])

    @classmethod
    def from_json(cls, data):
        """
        Inputs:
          data: JSON structure
            fields:
              image: Link to rgb formatted png
              mapping: Mapping from rgb colour string to a database key for the
                       corresponding rock.

            example:
                    {"image": "https://www.modelr.io/_gh/testimg.png,
                     "mapping": {"rgb(100,120,150)": ROCKDBKEY,
                                 "rgb(110,160,150)": ROCKDBKEY},
                     "z": }
        """

        response = requests.get(data["image"])
        image = StringIO(response.content)

        mapping = cls.fill_mapping(image, data["mapping"])

        return cls(image, mapping)

    def _make_data(self, var):

        data = np.zeros(self.image.shape)
        for i, rock in self.map.iteritems():
            index = self.image == i
            layer = (randn(np.sum(index)) *
                     getattr(rock, var + "_std") + getattr(rock, var))

            np.place(data, index, layer)

        return data

    def _get_data(self, var):

        data = self._make_data(var)
        return data

    @property
    def vp(self):
        return self._get_data("vp")

    @property
    def rho(self):
        return self._get_data("rho")

    @property
    def vs(self):
        return self._get_data("vs")

    @property
    def rpp(self):

        rpp = reflectivity_array(self.vp, self.vs, self.rho, self.theta)

        return rpp

    def resample(self, dz):

        z1 = np.arange(self.image.shape[0]) * self.dz / 1000.0
        z2 = np.arange(0, self.zrange / 1000.0, dz)

        # Don't interpolate beyond the model
        z2 = z2[z2 < np.amax(z1)]

        f = interp1d(z1, self.image, kind='nearest',
                     axis=0)
        self.image = f(z2)
        self.dz = dz

        
    def rpp_t(self, dt):

        if self.domain == 'time':
            if dt == self.dz:
                return self.rpp
            else:
                raise Exception('sampling mismatch')
            
        
        vpt = depth_to_time(self.vp, self.vp, self.dz, dt)
        times = np.arange(vpt.shape[0]) * dt
        vst = depth_to_time(self.vs, self.vp, self.dz, times)
        rhot = depth_to_time(self.rho, self.vp, self.dz, times)

        rpp = reflectivity_array(vpt, vst, rhot, self.theta)
        return rpp


class ImageModelPersist(ImageModel):

    def __init__(self, datafile, *args, **kwargs):

        super(self.__class__, self).__init__(*args, **kwargs)

        self.datafile = datafile

    def _get_data(self, arg):

        with h5py.File(self.datafile) as f:
            if arg in f:
                return f[arg].value

        # Create field
        with h5py.File(self.datafile, 'w') as f:
            data = self._make_data(arg)
            f.create_dataset(arg, data=data)

            return data

    @property
    def rpp(self):
        
        with h5py.File(self.datafile) as f:

            if 'rpp' in f:
                return f['rpp'].value

        rpp = rpp = super(self.__class__, self).rpp
        with h5py.File(self.datafile, 'w') as f:
            f.create_dataset('rpp', data=rpp)

        return rpp
            
    def rpp_t(self, dt):

        with h5py.File(self.datafile) as f:

            if 'rpp_t' in f:
                return f['rpp_t'].value

        rpp_t = super(self.__class__, self).rpp_t(dt)
        
        with h5py.File(self.datafile, 'w') as f:

            f.create_dataset('rpp_t', data=rpp_t)

            return rpp_t

    @classmethod
    def from_json(cls, data):

        m = md5.new()
        m.update(json.dumps(data))

        datafile = "/opt/data/" + m.hexdigest() + '.tmp'
        response = requests.get(data["image"])
        image = StringIO(response.content)
        mapping = cls.fill_mapping(image, data["mapping"])

        return cls(datafile, image, mapping, zrange=data["zrange"],
                   theta=data["theta"], domain=data["domain"])







