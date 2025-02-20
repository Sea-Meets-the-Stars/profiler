
import numpy as np

import gsw
from gsw import conversions, density

from IPython import embed

def process_dict(ifloat:dict):

    for ss in range(ifloat['lat'].size):
        try:
            ifloat['depth'][ss,:] = -1*gsw.z_from_p(
                ifloat['p'][ss,:], ifloat['lat'][ss])
        except:
            embed(header='23 of gsw')
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