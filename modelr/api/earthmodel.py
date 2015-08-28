from PIL import Image
import numpy as np
from numpy.random import randn


class EarthModel(object):
    """
    Base class for modelling the physical properties of the earth

    Inputs
      extents: (x0,y0,z0,x1,y1,z1), default=(0,0,0,1,1,1)
          The corner locations of the model.
      units: str, default='SI'
          SI or Imperial
    """

    def __init__(self, extents=(0.0, 0.0, 0.0, 1.0, 1.0, 1.0),
                 units='SI', zaxis='time'):

        # define the corners of the model
        self.extents = extents

        self.units = units
        self.zaxis = zaxis


class Model1D(EarthModel):
    """
    Builds a 1D model from a list of rocks
    """
    def __init__(self, rocks, dz=1, *args, **kwargs):

        super(Model1D, self).__init__(*args, **kwargs)
        self.rocks = rocks
        self.dz = dz
        self.depth = sum([rock.thickness for rock in rocks])

    def _data(self, arg):

        nsamps = int(self.depth / self.dz)
        data = np.zeros(nsamps)

        index = 0
        for rock in self.rocks:
            layer_size = np.ceil(rock.thickness / self.dz)
            end_index = index + layer_size
            if end_index > data.size:
                end_index = data.size

            data[index:end_index] = getattr(rock, arg)
            index = end_index
        return data

    @property
    def vp(self):
        return self._data('vp')

    @property
    def vs(self):
        return self._data('vs')

    @property
    def rho(self):
        return self._data("rho")
