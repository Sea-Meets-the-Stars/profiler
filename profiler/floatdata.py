""" Simple Class to hold glider data """
import os
import glob

import numpy as np

from profiler import profilerdata

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

class SoloData(profilerdata.ProfilerData):
    """
    Class to hold a full, standard Spray
    """
    platform = 'Solo'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False, binned:bool=False):

        self.in_field = in_field
        self.base_key = 'bindata'
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']

        # Init
        profiledata.ProfileData.__init__(self, datafile, dataset)

        if binned:
            loading.load_binned_data(self)
        else:
            loading.load_raw_data(self)

class EMApexData(SoloData):
    """
    Class to hold a full, standard EM Apex
    """
    platform = 'EMApex'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []
