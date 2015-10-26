import requests
import numpy as np
from numpy.random import randn
from bruges.rockphysics import smith_fluidsub
from modelr.constants import WAVELETS
from bruges.filters import rotate_phase
from bruges.rockphysics import moduli_dict as moduli

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

        # payload = {"ls": True, "auth": cls.auth}
        r = requests.get(cls.url() + "?ls")

        if r.status_code == 200:
            return r.json()
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
            data = r.json()

            if type(data) is list:
                output = [cls.from_json(d) for d in data]
            else:
                output = cls.from_json(data)
        else:
            raise modelrAPIException

        return output

    @classmethod
    def from_json(cls, json):
        return cls(**json)

    @classmethod
    def url(cls):

        return modelrAPI.host + '/' + cls.handler


class Rock(modelrAPI):

    handler = 'rock'

    def __init__(self, vp=3500, vs=2000, rho=3000,
                 porosity=.2, vclay=None, kclay=None,
                 kqtz=None, vp_std=0.0,
                 vs_std=0.0, rho_std=0.0,
                 fluid=None, name="", *args, **kwargs):

        self.vp = vp
        self.vs = vs
        self.rho = rho
        self.porosity = porosity
        self.vclay = vclay
        self.kclay = kclay
        self.kqtz = kqtz
        self.name = name

        if type(fluid) is dict:
            self.fluid = Fluid.from_json(fluid)
        else:
            self.fluid = fluid

        # uncertainties
        self.vp_std = vp_std
        self.rho_std = rho_std
        self.vs_std = vs_std

    @property
    def phi(self):
        return self.porosity

    @property
    def moduli(self):
        return moduli(self.vp, self.vs, self.rho)


class Fluid(modelrAPI):
    handler = 'fluid'

    def __init__(self, rho_w, rho_hc, Kw, Khc, Sw):

        self.rho_w = rho_w
        self.rho_hc = rho_hc
        self.Kw = Kw
        self.Khc = Khc
        self.Sw = Sw

    @classmethod
    def from_json(cls, data):

        return cls(data["rho_w"], data["rho_hc"],
                   data["k_w"], data["k_hc"],
                   data["sw"])


class FluidSub1D(modelrAPI):
    handler = None

    def __init__(self, layers, dz):

        self.layers = layers
        self.dz = dz

        self._set_data()

    def _set_data(self):

        depth = sum([layer["thickness"] for layer in self.layers])
        n_samps = int(depth / self.dz)

        self.z = np.arange(n_samps) * self.dz

        names = ['vp', 'vs', 'rho', 'phi', 'vclay',
                 'Kclay', 'Kqtz',
                 'rhow', 'rhohc', 'Kw', 'Khc', 'Sw',
                 'rhow_sub', 'rhohc_sub', 'Kw_sub',
                 'Khc_sub', 'Sw_sub']
        output = np.zeros((n_samps,),
                          dtype={"names": names,
                                 "formats": ['f4' for item in names]})

        i = 0
        for layer in self.layers:

            j = i + np.ceil(layer["thickness"] / self.dz)
            if j > n_samps:
                j = n_samps

            rock = layer["rock"]
            output["vp"][i:j] = randn(j - i) * rock.vp_std + rock.vp
            output["vs"][i:j] = randn(j - i) * rock.vs_std + rock.vs
            output["rho"][i:j] = randn(j - i) * rock.rho_std + rock.rho
            output["phi"][i:j] = rock.phi
            output["vclay"][i:j] = rock.vclay
            output["Kclay"] = rock.kclay
            output["Kqtz"] = rock.kqtz

            if rock.fluid:
                output["rhow"][i:j] = rock.fluid.rho_w
                output["rhohc"][i:j] = rock.fluid.rho_hc
                output["Kw"][i:j] = rock.fluid.Kw
                output["Khc"][i:j] = rock.fluid.Khc
                output["Sw"][i:j] = rock.fluid.Sw

                output["rhow"][i:j] = rock.fluid.rho_w
                output["rhohc"][i:j] = rock.fluid.rho_hc
                output["Kw"][i:j] = rock.fluid.Kw
                output["Khc"][i:j] = rock.fluid.Khc
                output["Sw"][i:j] = rock.fluid.Sw

                # fill in the substitution fluids
                k = i
                for subfluid in layer["subfluids"]:
                    l = k + np.ceil(subfluid["thickness"] / self.dz)
                    fluid = subfluid["fluid"]
                    output["rhow_sub"][k:l] = fluid.rho_w
                    output["rhohc_sub"][k:l] = fluid.rho_hc
                    output["Kw_sub"][k:l] = fluid.Kw
                    output["Khc_sub"][k:l] = fluid.Khc
                    output["Sw_sub"][k:l] = fluid.Sw

                    # TODO use a generator
                    k = l

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
        "layers": [{"rock": rock_json, "thickness": 100.0,
                    "subfluids": [{'fluid': fluid_json, "thickness": 50.0},
                      {'fluid_key': fluid_json, "thickness": 50.0}]},
                   {"rock_key": rock_json, "thickness": 100.0,
                    "subfluids":[{'fluid_key': fluid_json, "thickness": 50.0},
                              {'fluid_key': fluid_json, "thickness": 50.0}]}]}
        """

        layers = []
        for layer in data["layers"]:

            rock = Rock.from_json(layer["rock"])
            thickness = float(layer["thickness"])
            subfluids = [{"fluid": Fluid.from_json(subfluid["fluid"]),
                          "thickness": float(subfluid["thickness"])}
                         for subfluid in layer["subfluids"]]

            layer_dict = {"rock": rock,
                          "thickness": thickness,
                          "subfluids": subfluids}
            layers.append(layer_dict)

        return cls(layers, data["dz"])

    def smith_sub(self):
        """
        Returns vp, vs, rho using smith fluid substition
        """

        vp, vs, rho = smith_fluidsub(
            self.vp, self.vs, self.rho, self.phi,
            self.rhow, self.rhohc, self.Sw,
            self.Sw_sub, self.Kw, self.Khc,
            self.Kclay, self.Kqtz,
            vclay=self.vclay,
            rhownew=self.rhow_sub,
            rhohcnew=self.rhohc_sub,
            kwnew=self.Kw_sub, khcnew=self.Khc_sub)

        vp[~np.isfinite(vp)] = self.vp[~np.isfinite(vp)]
        vs[~np.isfinite(vs)] = self.vs[~np.isfinite(vs)]
        rho[~np.isfinite(rho)] = self.rho[~np.isfinite(rho)]

        return (vp, vs, rho)

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
    def Kclay(self):
        return self.data["Kclay"]

    @property
    def Kqtz(self):
        return self.data["Kqtz"]

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


class Seismic(modelrAPI):

    @classmethod
    def get(self, keys):
        pass

    def __init__(self, wavelet='ricker', dt=0.001,
                 frequency=20.0,
                 phase=0.0, snr=40.0, theta=[0],
                 wavelet_duration=0.5,
                 **kwargs):

        self.wavelet = WAVELETS[wavelet]
        self.dt = dt
        self.wavelet_duration = wavelet_duration
        self.f = float(frequency)
        self.snr = snr
        self.phase = phase
        self.theta = theta

    @property
    def src(self):

        return rotate_phase(
            self.wavelet(self.wavelet_duration, self.dt, self.f), self.phase)

