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

    Class attributes:
        auth: The private access key provided by modelr
        host: The host url for the database server
    """
    host = "http://localhost:8080"
    auth = 0

    @classmethod
    def ls(cls):
        """
        List all available authorized class entities

        Returns:
          A list of simple entity descriptions.
          example:
             [{"name": "NAME", "description": "DESCR",
               "key": "DATABASEKEY"},
              {"name": "NAME", "description": "DESCR",
               "key": "DATABASEKEY"}]
        """

        payload = {"ls": True, "auth": cls.auth}
        r = requests.get(cls.url, params=payload)

        if r.status_code == 200:
            return r.json
        else:
            raise modelrAPIException

    @classmethod
    def get(cls, keys):
        """
        Retrieves data from the modelr database and returns python objects.

        Inputs:
          keys (list): A list of database keys to retrieve.

        Returns:
          A list of python objects corresponding to the database keys.
          Keys with failed queries will be None.
        """

        payload = {"keys": keys, "auth": cls.auth}
        r = requests.get(cls.url(), params=payload)

        if r.status_code == 200:
            output = []
        for data in r.json():
            output.append(cls.from_json(data))
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
                                 "rgb(110,160,150)": ROCKDBKEY}}
        """

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


class FluidSub1D(modelrAPI):
    handler = None

    def __init__(self, layers, dz):

        self.layers = layers
        self.dz = dz

        self._set_data()

    def _set_data(self):

        depth = sum([layer.thickness for layer in self.layers])
        n_samps = int(depth / self.dz)

        names = ['vp', 'vs', 'rho', 'phi', 'vclay',
                 'rhow', 'rhohc', 'Kw', 'Khc', 'Sw',
                 'rhow_sub', 'rhohc_sub', 'Kw_sub',
                 'Khc_sub', 'Sw_sub']
        output = np.zeros((n_samps,),
                          dtype={"names": names,
                                 "formats": ['f4' for item in names]})

        i = 0
        for layer in self.layers:

            j = i + np.ceil(layer["thickness"] / self.dz)

            rock = layer["rock"]
            output["vp"][i:j] = randn(j - i) * rock.vp_std + rock.vp
            output["vs"][i:j] = randn(j - i) * rock.vs_std + rock.vs
            output["rho"][i:j] = randn(j - i) * rock.rho_std + rock.rho
            output["phi"][i:j] = rock.phi
            output["vclay"][i:j] = rock.vclay

            output["rhow"][i:j] = rock.fluid.rhow
            output["rhohc"][i:j] = rock.fluid.rhohc
            output["Kw"][i:j] = rock.fluid.Kw
            output["Khc"][i:j] = rock.fluid.Khc
            output["Sw"][i:j] = rock.fluid.Sw

            output["rhow"][i:j] = rock.fluid.rhow
            output["rhohc"][i:j] = rock.fluid.rhohc
            output["Kw"][i:j] = rock.fluid.Kw
            output["Khc"][i:j] = rock.fluid.Khc
            output["Sw"][i:j] = rock.fluid.Sw

            if layer["subfluids"]:
                k = i
                for subfluid in layer["subfluids"]:
                    l = k + np.ceil(subfluid.thickness / subfluid.dz)
                    fluid = subfluid.fluid
                    output["rhow_sub"][k:l] = fluid.rhow
                    output["rhohc_sub"][k:l] = fluid.rhohc
                    output["Kw_sub"][k:l] = fluid.Kw
                    output["Khc_sub"][k:l] = fluid.Khc
                    output["Sw_sub"][k:l] = fluid.Sw

                    # TODO use a generator
                    k = l
            else:
                output["rhow"][i:j] = rock.fluid.rhow
                output["rhohc"][i:j] = rock.fluid.rhohc
                output["Kw"][i:j] = rock.fluid.Kw
                output["Khc"][i:j] = rock.fluid.Khc
                output["Sw"][i:j] = rock.fluid.Sw

            # TODO use a generator
            i = j

        self.data = output

    def get(self, keys):
        """
        Not implemented
        """
        raise modelrAPIException

    @classmethod
    def from_json(cls, data):
        """
        data: json structure.

        example
       {"dz": 1.0,
        "layers": [{"rock_key": ROCKDBKEY, "thickness": 100.0,
                    "subfluids": [{'fluid_key': FLUIDDBKEY, "thickness": 50.0},
                      {'fluid_key': FLUIDDBKEY, "thickness": 50.0}]},
                   {"rock_key": ROCKDBKEY, "thickness": 100.0,
                    "subfluids":[{'fluid_key': FLUIDDBKEY, "thickness": 50.0},
                               {'fluid_key': FLUIDDBKEY, "thickness": 50.0}]}]}
        """

        layers = []
        for layer in data["layers"]:

            layer_dict = {}
            rock = Rock.get(layer["rock_key"])
            thickness = layer["thickness"]
            subfluids = [{"fluid": Fluid.get(fluid["fluid_key"]),
                          "thickness": fluid["thickness"]}
                         for fluid in layer["subfluids"]]

            layer_dict.update(rock=rock, thickness=thickness,
                              subfluids=subfluids)
            layers.append(layer_dict)

        return cls(layer_dict, data["dz"])

    def smith_sub(self):
        """
        Returns vp, vs, rho using smith fluid substition
        """
        
    @property
    def vp(self):
        return self.data["vp"]

    @property
    def rho(self):
        return self.data["rho"]

    @property
    def vs(self):
        return self.data["vs"]

    @property
    def phi(self):
        return self.data["phi"]

    @property
    def vclay(self):
        return self.data["vclay"]

    @property
    def rhow(self):
        return self.data["rhow"]

    @property
    def rhohc(self):
        return self.data["rhohc"]

    @property
    def Kw(self):
        return self.data["Kw"]

    @property
    def Khc(self):
        return self.data["Khc"]

    @property
    def Sw(self):
        return self.data["Sw"]

    @property
    def rhow_sub(self):
        return self.data["rhow_sub"]

    @property
    def rhohc_sub(self):
        return self.data["rhohc_sub"]

    @property
    def Kw_sub(self):
        return self.data["Kw_sub"]

    @property
    def Khc_sub(self):
        return self.data["Khc_sub"]

    @property
    def Sw_sub(self):
        return self.data["Sw_sub"]
