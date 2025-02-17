""" Simple Class to hold glider data """
import os
import glob

import numpy as np
import warnings

from profiler.utils import loading
from profiler import profiledata
from profiler.utils import apex_utils

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
    if dataset == 'ARCTERX-Leg2':
        # Solo
        dfiles = glob.glob(
            '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Solo/*.mat')
        solo = SoloData.from_list(dfiles, dataset, in_field=True)
        # EM Apex
        dfiles = glob.glob(
            '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/EM_Apex/*.npz')
        em_apex = EMApexData.from_list(dfiles, dataset, in_field=True)
        #
        return [solo, em_apex]
    else:
        raise IOError(f"Not ready for this dataset: {dataset}")

class SoloData(profiledata.ProfileData):
        """
        Class to hold a full, standard Spray
        """
        dtype = 'Solo'

        in_field:bool = None
        base_key:str = None

        scalar_keys:list = []

        def __init__(self, datafile:str, dataset:str,
                     in_field:bool=False):

            self.in_field = in_field
            self.base_key = 'bindata'
            self.profile_arrays = ['lat', 'lon', 'time']
            self.depth_arrays = ['depth']
            self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']

            # Init
            profiledata.ProfileData.__init__(self, datafile, dataset)

            loading.load_binned_data(self)

        def __repr__(self):
            """ Return the representation of the CTDData object """
            rstr = f"SoloData object for {self.dataset}\n"
            rstr += f"  Number of profiles: {len(self.time)}\n"
            rstr += f"  Time range: {self.time.min()} to {self.time.max()}\n"
            # Variables
            rstr += "  Variables:\n"
            for key in self.depth_arrays:
                rstr += f"    {key}: {getattr(self, key).shape}\n"
            for key in self.profile_arrays:
                rstr += f"    {key}: {getattr(self, key).shape}\n"
            for key in self.profile_depth_arrays:
                rstr += f"    {key}: {getattr(self, key).shape}\n"
            return rstr



class EMApexData(SoloData):
        """
        Class to hold a full, standard EM Apex
        """
        dtype = 'EMApex'

        in_field:bool = None
        base_key:str = None

        scalar_keys:list = []

        def __init__(self, datafile:str, dataset:str,
                     in_field:bool=False):

            self.in_field = in_field
            self.base_key = 'bindata'
            self.profile_arrays = ['lat', 'lon', 'time']
            self.depth_arrays = ['depth']
            self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']

            # Init
            profiledata.ProfileData.__init__(self, datafile, dataset)

            loading.load_binned_data(self)

        def __repr__(self):
            """ Return the representation of the EMApex object """
            # Call the super
            rstr = super().__repr__()
            rstr.replace('Solo', 'EMApex')
            #
            return rstr