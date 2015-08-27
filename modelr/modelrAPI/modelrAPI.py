import requests
from StringIO import StringIO
import numpy as np
from PIL import Image
from numpy.random import randn


class modelrAPIException(Exception):
    pass


class modelrAPI(object):
    """
    API for accessing the modelr app database.

    Args
        auth: The private access key provided by modelr
    """
    host = "http://localhost:8080"
    auth = 0

    @classmethod
    def list(cls):

        payload = {"ls": True, "auth": cls.auth}
        r = requests.get(cls.url, params=payload)

        if r.status_code == 200:
            return r.json
        else:
            raise modelrAPIException

    @classmethod
    def get(cls, keys):

        payload = {"keys": keys, "auth": cls.auth}
        r = requests.get(cls.url(), params=payload)

        if r.status_code == 200:
            output = []
            output.append(cls.from_json(r.json()))
        else:
            raise modelrAPIException

        if len(output) == 1:
            output = output[0]
        return output

    @classmethod
    def from_json(cls, json):
        return cls(**json)

    @classmethod
    def url(cls):

        return modelrAPI.host + '/' + cls.handler


class Rock(modelrAPI):

    handler = 'rock'

    def __init__(self, vp, vs, rho, porosity,
                 vclay, vp_std=0.0,
                 vs_std=0.0, rho_std=0.0, **kwargs):

        self.vp = vp
        self.vs = vs
        self.rho = rho
        self.porosity = porosity
        self.vclay = vclay

        # uncertainties
        self.vp_std = vp_std
        self.rho_std = rho_std
        self.vs_std = vs_std


class Fluid(modelrAPI):
    handler = 'fluid'

    def __init__(self, rho_w, rho_hc, Kw, Khc, Sw):

        self.rho_w = rho_w
        self.rho_hc = rho_hc
        self.Kw = Kw
        self.Khc = Khc
        self.Sw = Sw


class ImageModel(modelrAPI):
    handler = 'earth_model'

    def __init__(self, image, mapping,
                 extents=(0.0, 0.0, 0.0, 0.0),
                 units="SI"):

        self.units = units
        self.extents = extents

        # Change the mapping from RGB to index
        image = Image.open(image)
        index_mapping = {}
        for colour, rock in mapping.iteritems():
            rgb = np.array([[colour.split('(')[1].split(')')[0].split(',')]],
                           'uint8')

            index = np.asarray(Image.fromarray(rgb)
                               .quantize(palette=image)).flatten()[0]
            index_mapping[index] = rock

        self.map = index_mapping
        self.image = np.asarray(image.convert("P"))

    @classmethod
    def from_json(cls, data):

        response = requests.get(data["image"])
        image = StringIO(response.content)

        # Change from rock keys to rock objects in the mapping
        mapping = data["mapping"]
        for colour, data in mapping.iteritems():
            rock = Rock.get(data["key"])
            mapping[colour] = rock

        return cls(image, mapping)

    def _get_data(self, var):

        data = np.zeros(self.image.shape)
        for i, rock in self.map.iteritems():
            index = self.image == 1
            layer = (randn(np.sum(index)) *
                     getattr(rock, var + "_std") + getattr(rock, var))

            np.place(data, index, layer)
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
