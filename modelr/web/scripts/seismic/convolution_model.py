from modelr.reflectivity import do_convolve
from modelr.api import FluidSub1D, Seismic

import numpy as np


def run_script(json_payload):

    # parse json
    earth_model = FluidSub1D.from_json(json_payload["earth_model"])
    seismic = Seismic.from_json(json_payload["seismic"])

    data = do_convolve(seismic.src, earth_model.rpp_t(seismic.dt))

    payload = {"seismic": data, "dt": seismic.dt,
               "min": np.amin(data), "max": np.amax(data),
               "dx": earth_model.dx}

    return payload
