""" Simple Class to hold glider data """
import os
import glob

import numpy as np
import warnings

from cugn import idg_utils
from cugn import profiledata

from IPython import embed

def load_dataset(dataset:str):
    """
    Load a dataset based on the provided dataset name.

    Parameters:
        dataset (str): The name of the dataset to load.

    Returns:
        cData (CTDData): The loaded CTDData object.

    Raises:
        ValueError: If the provided dataset is not supported.
    """
    if dataset == 'ARCTERX':
        dfile = os.path.join(
            os.getenv('OS_SPRAY'), 'ARCTERX', 'arcterx_ctd.mat')
    elif dataset == 'ARCTERX-Leg2':
        dfiles = glob.glob(os.path.join(
            os.getenv('OS_SPRAY'), 'ARCTERX', 'Leg2', '*.mat'))
        return SprayData.from_list(dfiles, dataset, adcp_on=False, in_field=True)
    elif dataset == 'Calypso2019':
        dfile = os.path.join(
            os.getenv('OS_SPRAY'), 'Calypso', 'calypso2019_ctd.mat')
    elif dataset == 'Calypso2022':
        dfile = os.path.join(
            os.getenv('OS_SPRAY'), 'Calypso', 'calypso2022_ctd.mat')
    else: 
        raise ValueError(f"Dataset {dataset} not supported")

    # Load
    cData = SprayData(dfile, dataset)

    # Survey specific cuts
    if dataset == 'Calypso2022':
        warnings.warn("Trimming last 3 weeks of Calypso2022 data")
        # Trim the last 3 weeks
        maxt = np.max(cData.time)
        mint = np.min(cData.time)
        goodt = cData.time < (maxt - 12*24*3600)
        goodt &= (cData.time > (mint + 3*24*3600))
        cData = cData.profile_subset(np.where(goodt)[0], init=False)

    return cData

class SprayData(profiledata.ADCPData):
        """
        Class to hold a full, standard Spray
        """
        dtype = 'Spray'

        in_field:bool = None
        base_key:str = None

        scalar_keys:list = []

        def __init__(self, datafile:str, dataset:str,
                     adcp_on:bool=True, in_field:bool=False):

            # Init
            self.profile_arrays = ['lat', 'lon', 'time']
            self.depth_arrays = ['depth']
            self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']

            self.in_field = in_field
            if self.in_field:
                self.base_key = 'bindata'
            else:
                self.base_key = 'ctd'

            self.profile_depth_arrays += ['theta']

            # Init
            profiledata.ADCPData.__init__(self, datafile, dataset,
                                          adcp_on=adcp_on)

            # Load
            idg_utils.load_binned_data(self)

        def __repr__(self):
            """ Return the representation of the CTDData object """
            rstr = f"SprayData object for {self.dataset}\n"
            rstr += f"  Number of profiles: {len(self.time)}\n"
            rstr += f"  Time range: {self.time.min()} to {self.time.max()}\n"
            # Settings (adcp_on, in_field)
            rstr += f"  In field? {self.in_field}"
            rstr += f"  ADCP on? {self.adcp_on}"
            # Variables
            rstr += "  Variables:\n"
            for key in self.depth_arrays:
                rstr += f"    {key}: {getattr(self, key).shape}\n"
            for key in self.profile_arrays:
                rstr += f"    {key}: {getattr(self, key).shape}\n"
            for key in self.profile_depth_arrays:
                rstr += f"    {key}: {getattr(self, key).shape}\n"
            return rstr

