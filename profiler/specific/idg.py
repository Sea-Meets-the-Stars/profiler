""" methods related to the IDG at SIO """
#import pymatreader
from profiler.loading.pymatreader import pymatreader

import numpy as np

from IPython import embed


def load_raw(datafile:str):
    """ Load raw data from a file

    Args:
        datafile (str): The path to the data file.

    Returns:
        dict, dict: The data dictionary and the dictionary of arrays.
    """

    # Load
    f = pymatreader.read_mat(datafile)
    data = f['data']

    #
    darrays = {}
    iprof = {}
    # Count em
    nDepths = [len(item) for item in data['t']]
    Nprof = len(data['t'])
    Ndepth = np.max(nDepths)
    
    # Profile arrays
    darrays['profile_arrays'] = ['time', 'lat', 'lon']
    for key in darrays['profile_arrays']:
        iprof[key] = data[key][:,1]

    # Depth arrays
    darrays['depth_arrays'] = []

    darrays['profile_depth_arrays'] = ['t', 's', 'depth', 
                                       'theta', 'sigma', 'rho', 'p']
    # Profile + Depth arrays
    for key in darrays['profile_depth_arrays']:
        if key not in iprof:
            iprof[key] = np.ones((Nprof, Ndepth))*np.nan
        for pp in range(Nprof):
            iprof[key][pp, :nDepths[pp]] = data[key][pp]

    # Qual vals
    iprof['qual'] = {}
    for key in ['t', 's', 'depth', 'theta', 'sigma', 'rho', 'p']:
        if key == 't':
            iprof['qual'][key] = data['qual'][key]
        else:
            iprof['qual'][key] = data['qual']['s']

    # Return
    return iprof, darrays