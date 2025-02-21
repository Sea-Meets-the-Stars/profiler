
from profiler.floatdata import EMApexData

import pymatreader

import numpy as np

import gsw
from gsw import conversions, density

from profiler.floatdata import EMApexData
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
    Load the EMApex data for infield processing

    Args:
        datafile (str): The path to the EMApex data file.

    Returns:
        list: A list of  EMApexData objects containing the data from the given file.
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
        emApex = EMApexData.from_dict(float_dict, darrays, mdict,
                                      dataset, in_field=True)

        # Add qual
        emApex.qual = float_dict['qual']

        # Bin?
        if binme:
            emApex = binning.bin_profilerdata(
                emApex, add_vel=add_vel)
        # Finish
        pDatas.append(emApex)
        if debug:
            break

    # Return
    return pDatas

def process_alto_float(d:dict, ss:int):

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
    ifloat['time'] = ((d['dn_beg'][ss]+d['dn_end'][ss])/2. - 719529) * 86400
    ifloat['lat'] = (d['lat_beg'][ss]+d['lat_end'][ss])/2.
    ifloat['lon'] = (d['lon_beg'][ss]+d['lon_end'][ss])/2.

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
            