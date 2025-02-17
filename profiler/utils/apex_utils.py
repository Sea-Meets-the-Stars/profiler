""" Apex utility methods """

import numpy as np

import gsw
from gsw import conversions, density

import pymatreader

from IPython import embed

def process_em_apex_float(ifloat:dict):
    # Most of these are for the binning software
    #   which will be REFACTORED!

    # Rename
    ifloat['t'] =  ifloat.pop('te')
    ifloat['s'] =  ifloat.pop('sa')

    # Replace time with time_prof!
    #   And convert to Unix time
    ifloat['time'] =  (ifloat.pop('time_prof') - 719529) * 86400

    # Depth
    ifloat['depth'] = np.zeros_like(ifloat['t'])

    for ss in range(ifloat['lat'].size):
        ifloat['depth'][:,ss] = -1*gsw.z_from_p(ifloat['pr'][:,ss], 
                        ifloat['lat'][ss])
        # SA
        ifloat['SA'] = conversions.SA_from_SP(
            ifloat['s'], ifloat['pr'], 
            ifloat['lon'][ss], 
            ifloat['lat'][ss])

        # theta -- Potential Temperature
        ifloat['theta'] = gsw.pt0_from_t(
            ifloat['SA'], 
            ifloat['t'], 
            ifloat['pr'])

        # CT
        CT = gsw.CT_from_t(
            ifloat['SA'], 
            ifloat['t'], ifloat['pr'])

        # sigma -- Potential Density
        ifloat['sigma'] = density.sigma0(
            ifloat['SA'], CT)

        # rho -- In-situ Density
        ifloat['rho'] = density.rho(
            ifloat['SA'], CT, ifloat['pr'])

    # Convert to lists and add dummy qual
    ifloat['qual'] = {}
    for key in ['t', 's', 'depth', 'SA', 'theta', 'sigma', 'rho']:
        ifloat[key] = [item for item in ifloat[key].T]
        # qual
        ifloat['qual'][key] = []
        for profile in range(len(ifloat[key])):
            qual_vals = np.isnan(ifloat[key][profile]).astype(int)*10000
            ifloat['qual'][key].append(qual_vals) 

    # Replicate lat, lon, time (for the binning code)
    for key in ['lat', 'lon', 'time']:
        ifloat[key] = np.stack([ifloat[key],ifloat[key]]).T

    return ifloat
            
def process_apex_floats(matfile:str, debug:bool=False):
    """ Process the APEX floats in the provided matfile """     
    # Load
    d = pymatreader.read_mat(matfile)

    float_dict = {}
    for ifloat in d['E'].keys():
        print(f"Working on float {ifloat}")
        float_dict[ifloat] = process_em_apex_float(
            d['E'][ifloat])
        if debug:
            break

    # Return
    return float_dict