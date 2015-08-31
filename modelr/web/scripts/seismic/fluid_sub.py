from modelr.api import Seismic, FluidSub1D
from bruges.reflection import zoeppritz_rpp as zoep
from bruges.transform import depth_to_time
from modelr.reflectivity import do_convolve
import json
import numpy as np


def run_script(json_payload):

    # parse json
    fs_model = FluidSub1D.from_json(json_payload["earth_model"])
    seismic = Seismic.from_json(json_payload["seismic"])

    # extract rock properties
    vp, vs, rho = (fs_model.vp, fs_model.vs, fs_model.rho)
    vp_sub, vs_sub, rho_sub = fs_model.smith_sub()

    # convert to time
    dt = seismic.dt
    dz = fs_model.dz
    z = fs_model.z
    index = np.arange(vp.size, dtype=int)
    t_index = depth_to_time(index, vp, dz, dt).astype(int)
    sub_t_index = depth_to_time(index, vp_sub, dz, dt).astype(int)
    vp_t, vs_t, rho_t = (vp[t_index], vs[t_index], rho[t_index])
    vp_sub_t, vs_sub_t, rho_sub_t = (vp_sub[sub_t_index],
                                     vs_sub[sub_t_index],
                                     rho_sub[sub_t_index])

    # calculate reflectivities
    rpp = np.nan_to_num(np.array([zoep(vp_t[:-1], vs_t[:-1], rho_t[:-1],
                                       vp_t[1:], vs_t[1:], rho_t[1:],
                                       float(theta))
                                  for theta in seismic.theta[::-1]]).T)

    rpp_sub = np.nan_to_num(np.array([zoep(vp_sub_t[:-1], vs_sub_t[:-1],
                                           rho_sub_t[:-1],
                                           vp_sub_t[1:], vs_sub_t[1:],
                                           rho_sub_t[1:], float(theta))
                                      for theta in seismic.theta[::-1]]).T)

    # trim to be the same size
    n = min(rpp.shape[0], rpp_sub.shape[0])
    print n, rpp.shape, np.amax(rpp)
    rpp = rpp[:n, :]
    rpp_sub = rpp_sub[:n, :]
    t = np.arange(n) * dt

    # create synthetic seismic
    traces = np.squeeze(do_convolve(seismic.src, rpp[:, np.newaxis, :]))
    sub_traces = np.squeeze(do_convolve(seismic.src,
                                        rpp_sub[:, np.newaxis, :]))

    output = {"vp": vp.tolist(), "vs": vs.tolist(),
              "rho": rho.tolist(), "vp_sub": vp_sub.tolist(),
              "vs_sub": vs_sub.tolist(), "rho_sub": rho_sub.tolist(),
              "synth": np.nan_to_num(traces).tolist(),
              "synth_sub": np.nan_to_num(sub_traces).tolist(),
              "theta": seismic.theta,
              "rpp": rpp[:,0].tolist(),
              "rpp_sub": rpp_sub[:,0].tolist(),
              "t_lim": [float(np.amin(t)), float(np.amax(t))],
              "z_lim": [float(np.amin(z)), float(np.amax(z))],
              "vp_lim": [float(np.amin((vp, vp_sub))),
                         float(np.amax((vp, vp_sub)))],
              "vs_lim": [float(np.amin((vs, vs_sub))),
                         float(np.amax((vs, vs_sub)))],
              "rho_lim": [float(np.amin((rho, rho_sub))),
                          float(np.amax((rho, rho_sub)))],
              "rpp_lim": [float(np.amin((rpp, rpp_sub))),
                          float(np.amax((rpp, rpp_sub)))],
              "synth_lim": [float(np.amin((traces, sub_traces))),
                            float(np.amax((traces, sub_traces)))]}

    return json.dumps(output)
