
from profiler.floatdata import EMApexData

import pymatreader

import numpy as np

import gsw
from gsw import conversions, density

from profiler.floatdata import EMApexData
from profiler import binning

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
            emApex = binning.bin_profilerdata(
                emApex, add_vel=add_vel)
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
        ifloat[key] = np.zeros_like(ifloat['t'])
        darrays['profile_depth_arrays'].append(key)

    for ss in range(ifloat['lat'].size):
        ifloat['depth'][ss,:] = -1*gsw.z_from_p(ifloat['p'][ss,:], 
                        ifloat['lat'][ss])
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

    # Return
    return ifloat, darrays
            