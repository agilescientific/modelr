from modelr.reflectivity import do_convolve
from modelr.api import ImageModelPersist, Seismic

import numpy as np


def run_script(json_payload):

    # parse json
    earth_model = ImageModelPersist.from_json(json_payload["earth_model"])
    seismic = Seismic.from_json(json_payload["seismic"])

    data = do_convolve(seismic.src, earth_model.rpp_t(seismic.dt)).squeeze()

    payload = {"seismic": data[..., 0].T.tolist(), "dt": seismic.dt,
               "min": float(np.amin(data)), "max": float(np.amax(data)),
               "dx": earth_model.dx}

    return payload
