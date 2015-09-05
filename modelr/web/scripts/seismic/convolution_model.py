from modelr.reflectivity import do_convolve
from modelr.api import ImageModelPersist, Seismic

import numpy as np


def run_script(json_payload):

    try:

        # parse json
        earth_model = ImageModelPersist.from_json(json_payload["earth_model"])
        seismic = Seismic.from_json(json_payload["seismic"])

        trace = json_payload["trace"]
        offset = json_payload["offset"]

        # seismic
        data = do_convolve(seismic.src,
                           earth_model.rpp_t(seismic.dt)[..., offset]
                           [..., np.newaxis]).squeeze()

        # Hard coded, could be changed to be part of the seismic object
        f0 = 4.0
        f1 = 100.0
        f = np.logspace(max(np.log2(f0), np.log2(7)),
                        np.log2(f1), 50,
                        endpoint=True, base=2.0)
        wavelets = seismic.wavelet(.1, seismic.dt, f)
        wavelet_gather = do_convolve(wavelets,
                                     earth_model.rpp_t(seismic.dt)
                                     [..., trace, offset]
                                     [..., np.newaxis, np.newaxis]).squeeze()
        
        offset_gather = do_convolve(
            seismic.src, earth_model.rpp_t(seismic.dt)[..., trace, :]
            [..., np.newaxis, ...]).squeeze()
    
        payload = {"seismic": data.T.tolist(), "dt": seismic.dt,
                   "min": float(np.amin(data)), "max": float(np.amax(data)),
                   "dx": earth_model.dx,
                   "wavelet_gather": wavelet_gather.T.tolist(),
                   "offset_gather": offset_gather.T.tolist()}

        return payload
    except Exception as e:
        print 'KLFSJDKLJSDL', e
