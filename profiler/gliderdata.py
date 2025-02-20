""" Simple Class to hold glider data """
import os
import glob

import numpy as np
import warnings
import xarray

from profiler import profilerdata
from profiler.loading import binned
from profiler.loading import load_raw

from IPython import embed

def load_dataset(dataset:str):
    """
    Load a dataset based on the provided dataset name.

    Parameters:
        dataset (str): The name of the dataset to load.

    Returns:
        list: List of profilerdata.ProfilerData objects

    Raises:
        ValueError: If the provided dataset is not supported.
    """
    if dataset == 'ARCTERX':
        dfile = os.path.join(
            os.getenv('OS_SPRAY'), 'ARCTERX', 'arcterx_ctd.mat')
    elif dataset == 'ARCTERX-Leg2':
        dfiles = glob.glob(os.path.join(
            os.getenv('OS_SPRAY'), 'ARCTERX', 'Leg2', '*.mat'))

        pDatas = []
        for dfile in dfiles:
            sData =  SprayData.from_binned_file(
                    dfiles, 'idg', dataset, in_field=True)
            pDatas.append(
            )
    elif dataset == 'Calypso2019':
        dfile = os.path.join(
            os.getenv('OS_SPRAY'), 'Calypso', 'calypso2019_ctd.mat')
    elif dataset == 'Calypso2022':
        dfile = os.path.join(
            os.getenv('OS_SPRAY'), 'Calypso', 'calypso2022_ctd.mat')
    else: 
        raise ValueError(f"Dataset {dataset} not supported")

    # Survey specific cuts
    if dataset == 'Calypso2022':
        raise IOError("FIX THIS")
        goodt = cData.time < (maxt - 12*24*3600)
        goodt &= (cData.time > (mint + 3*24*3600))
        cData = cData.profile_subset(np.where(goodt)[0], init=False)

    return pDatas

class SprayData(profilerdata.ADCPData):
    """
    Class to hold a full, standard Spray
    """
    dtype = 'Spray'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False):

        # Init
        self.profile_arrays = ['time', 'lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']

        self.in_field = in_field
        if not self.in_field:
            adcp_on:bool=True
        self.profile_depth_arrays += ['theta']

        # Init
        profilerdata.ADCPData.__init__(self, datafile, dataset)


    def rstr_settings(self):
        """ Return the representation of the CTDData object """
        # Settings (adcp_on, in_field)
        r_s = super().rstr_settings()

        # More settings
        r_s.append(f"  In field? {self.in_field}")
        r_s.append(f"  ADCP on? {self.adcp_on}")
        
        return r_s


class SlocumbData(profilerdata.ProfilerData):
    """
    Class to hold a full, standard Spray
    """
    platform = 'Slocumb'

    in_field:bool = None

    scalar_keys:list = []
    
    # Loader
    loader_dict = dict(t='temperature', s='salinity')

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False, binned:bool=False):

        # Init
        profilerdata.ProfilerData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'SA']
