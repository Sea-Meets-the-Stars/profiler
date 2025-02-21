
from profiler.floatdata import EMApexData

import pymatreader

import numpy as np

import gsw
from gsw import conversions, density

from profiler.floatdata import AltoData
from profiler import binning
from profiler.processing import gsw as profiler_gsw 

from IPython import embed

def load_infield(datafile:str, dataset:str, 
                        binme:bool=True,
                        debug:bool=False,
                        skip_floats:list=None,
                        missid_offset:int=0,
                        add_vel:bool=True):
    """
    Load the Alto data for infield processing

    Args:
        datafile (str): The path to the Alto float data file.
        dataset (str): The name of the dataset.
        binme (bool): Whether to bin the data or not.
        debug (bool): Whether to run in debug mode.
        skip_floats (list): A list of floats to skip.
        missid_offset (int): The offset to add to the float number to get the mission ID.
        add_vel (bool): Whether to add velocity data to the binned data.
        

    Returns:
        list: A list of  Alto objects containing the data from the given file.
    """
    d = pymatreader.read_mat(datafile)

    pDatas = []

    # Loop on floats
    for ss, flnum in enumerate(d['A']['flnum']):
        if skip_floats is not None and flnum in skip_floats:
            print(f"Skipping {flnum}")
            continue
        # Meta dict
        mdict = {}
        mdict['datafile'] = datafile
        mdict['missid'] = flnum + missid_offset
        #
        print(f"Working on float {flnum}")
        float_dict, darrays = process_alto_float(d['A'], ss)
        # Object me
        alto = AltoData.from_dict(float_dict, darrays, mdict,
                                      dataset, in_field=True)

        # Add qual
        alto.qual = float_dict['qual']

        # Bin?
        if binme:
            alto = binning.bin_profilerdata(alto)
        # Finish
        pDatas.append(alto)
        if debug:
            break

    # Return
    return pDatas

def process_alto_float(d:dict, ss:int):
    """ Process a single float from the Alto dataset

    Args:
        d (dict): dict of Alto data
        ss (int): index of the float to process

    Returns:
        dict, dict: The float data and the data arrays
    """

    nprof = len(d['profnum'][ss])
    
    ifloat = {}
    darrays = {}
    # Rename
    darrays['profile_depth_arrays'] = ['t', 's', 'p']
    ifloat['t'] = d['temp'][ss].T
    ifloat['s'] = d['sal'][ss].T
    ifloat['p'] =  np.outer(np.ones(nprof), d['pgrid'][0])


    # Replace time with time_prof!
    #   And convert to Unix time
    darrays['profile_arrays'] = ['time', 'lat', 'lon']

    # Prep time, lat, lon
    #  TODO -- Do this more precisely
    ifloat['time'] = ((d['dn_beg'][ss]+d['dn_end'][ss])/2. - 719529) * 86400
    ifloat['lat'] = (d['lat_beg'][ss]+d['lat_end'][ss])/2.
    ifloat['lon'] = (d['lon_beg'][ss]+d['lon_end'][ss])/2.

    # Add a random bit of time to the profile times
    ifloat['time'] += np.random.uniform(0, 1, size=nprof)

    # NaN out the bad profiles
    bad = np.zeros(nprof, dtype=bool)
    bad[d['j_badprofiles'][ss] - 1] = True
    for key in darrays['profile_arrays']:
        ifloat[key][bad] = np.nan

    # Depth arrays
    darrays['depth_arrays'] = []

    # Profile + Depth arrays
    for key in ['depth', 'sigma', 'rho', 'SA', 'theta']:
        ifloat[key] = np.ones_like(ifloat['t'])*np.nan
        darrays['profile_depth_arrays'].append(key)

    # GSW me
    profiler_gsw.process_dict(ifloat)

    # Return
    return ifloat, darrays
            