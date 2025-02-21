
import numpy as np

import gsw
from gsw import conversions, density

from IPython import embed

def process_dict(ifloat:dict):
    """ Process the data in the dictionary using gsw

    The fields in the dictionary are:
        lat, lon, time, s, t, p

    The following fields are added:
        depth, SA, theta, CT, sigma, rho

    Args:
        ifloat (dict): The dictionary of data to process.
    """

    for ss in range(ifloat['lat'].size):
        ifloat['depth'][ss,:] = -1*gsw.z_from_p(
            ifloat['p'][ss,:], ifloat['lat'][ss])
        # SA
        ifloat['SA'][ss,:] = conversions.SA_from_SP(
            ifloat['s'][ss,:], ifloat['p'][ss,:], 
            ifloat['lon'][ss], 
            ifloat['lat'][ss])
        
    # theta -- Potential Temperature
    ifloat['theta'] = gsw.pt0_from_t(
        ifloat['SA'], 
        ifloat['t'], 
        ifloat['p'])

    # CT
    CT = gsw.CT_from_t(
        ifloat['SA'], 
        ifloat['t'], ifloat['p'])

    # sigma -- Potential Density
    ifloat['sigma'] = density.sigma0(
        ifloat['SA'], CT)

    # rho -- In-situ Density
    ifloat['rho'] = density.rho(
        ifloat['SA'], CT, ifloat['p'])

    # Qual vals
    ifloat['qual'] = {}
    for key in ['t', 's', 'depth', 'SA', 'theta', 'sigma', 'rho', 'p']:
        # qual
        ifloat['qual'][key] = []
        for profile in range(len(ifloat[key])):
            qual_vals = np.isnan(ifloat[key][profile]).astype(int)*10000
            ifloat['qual'][key].append(qual_vals) 