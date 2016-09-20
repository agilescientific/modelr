from modelr.reflectivity import do_convolve
from modelr.api import ImageModelPersist, Seismic
from bruges.noise import noise_db
from bruges.filters import rotate_phase

import traceback

import numpy as np
import sys

def run_script(json_payload):
    """
    Calculates synthetic seismic data from a convolution model.
    Creates data for a cross section, angle gather, and wavelet gather.

    Inputs
    json_payload = {"earth_model": See ImageModel in modelr.api,
                    "seismic": See SeismicModel in modelr.api,
                    "trace": The trace number to use for the angle and
                             wavelet gathers.
                    "offset": The offset index to use for the wavelet
                              and seismic cross section.}
    """

    try:

        seismic = Seismic.from_json(json_payload["seismic"])
        
        # parse json
        earth_model = ImageModelPersist.from_json(json_payload["earth_model"])
        if earth_model.domain == 'time':
            earth_model.resample(seismic.dt)

        trace = json_payload["trace"]
        offset = json_payload["offset"]

        ph = seismic.phase
        src = seismic.src

        # seismic
        data = do_convolve(src,
                           earth_model.rpp_t(seismic.dt)[..., offset]
                           [..., np.newaxis]).squeeze()

        # angle gather
        offset_gather = do_convolve(src,
                                    earth_model.rpp_t(seismic.dt)[..., trace, :]
                                    [..., np.newaxis, ...]).squeeze()

        # frequency gather
        f0 = 4.0
        f1 = 100.0
        f = np.logspace(max(np.log2(f0), np.log2(7)),
                        np.log2(f1), 50,
                        endpoint=True, base=2.0)

        wavelets = rotate_phase(seismic.wavelet(seismic.wavelet_duration, seismic.dt, f),
                                ph,
                                degrees=True)

        wavelet_gather = do_convolve(wavelets,
                                     earth_model.rpp_t(seismic.dt)
                                     [..., trace, offset]
                                     [..., np.newaxis, np.newaxis]).squeeze()
        
        # add noise if required
        if seismic.snr:
            data += noise_db(data, seismic.snr)
            offset_gather += noise_db(offset_gather, seismic.snr)
            wavelet_gather += noise_db(wavelet_gather, seismic.snr)

        # METADATA
        metadata = {}
        metadata["moduli"] = {}
        for rock in earth_model.get_rocks():
            if rock.name not in metadata["moduli"]:
                metadata["moduli"][rock.name] = rock.moduli

        if earth_model.domain == "time":
            dt = earth_model.zrange / float(data.shape[0])
        else:
            dt = seismic.dt * 1000.0
            
        payload = {"seismic": data.T.tolist(),
                   "dt": dt,
                   "min": float(np.amin(data)),
                   "max": float(np.amax(data)),
                   "dx": earth_model.dx,
                   "wavelet_gather": wavelet_gather.T.tolist(),
                   "offset_gather": offset_gather.T.tolist(),
                   "f": f.tolist(),
                   "theta": earth_model.theta,
                   "metadata": metadata}

        return payload
    
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        
