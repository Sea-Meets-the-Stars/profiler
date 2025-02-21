
from profiler.floatdata import EMApexData

import pymatreader

import numpy as np


from profiler.floatdata import EMApexData
from profiler import binning
from profiler.processing import gsw as profiler_gsw 

from IPython import embed

def load_emapex_infield(datafile:str, dataset:str, 
                        binme:bool=True,
                        debug:bool=False,
                        skip_floats:list=None,
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
    floats = list(d['E'].keys())
    floats.sort()
    for ifloat in floats:
        # Skip one bad one 
        if ifloat == 'F9462':
            print("Skipping F9462")
            print("REMOVE THIS SOMEDAY!!!")
            continue
        if skip_floats is not None and ifloat in skip_floats:
            print(f"Skipping {ifloat}")
            continue
        # Meta dict
        mdict = {}
        mdict['datafile'] = datafile
        mdict['missid'] = int(ifloat[1:])
        #
        print(f"Working on float {ifloat}")
        float_dict, darrays = process_em_apex_float(d['E'][ifloat])
        # Object me
        emApex = EMApexData.from_dict(float_dict, darrays, mdict,
                                      dataset, in_field=True)

        # Add qual
        emApex.qual = float_dict['qual']

        # Bin?
        if binme:
            emApex = binning.bin_profilerdata(emApex)
        # Finish
        pDatas.append(emApex)
        if debug:
            break

    # Return
    return pDatas

def process_em_apex_float(ifloat:dict):

    #
    darrays = {}
    # Rename
    darrays['profile_depth_arrays'] = ['t', 's', 'p']
    ifloat['t'] =  ifloat.pop('te').T
    ifloat['s'] =  ifloat.pop('sa').T
    ifloat['p'] =  ifloat.pop('pr').T

    # Replace time with time_prof!
    #   And convert to Unix time
    ifloat['time'] =  (ifloat.pop('time_prof') - 719529) * 86400
    darrays['profile_arrays'] = ['time', 'lat', 'lon']

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
            