""" Simple Class to hold glider data """
import os
import glob

import numpy as np

from profiler import profilerdata
from profiler.specific import idg

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
                    in_field:bool=False):

        # Init
        profilerdata.ProfilerData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.base_key = 'bindata'
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']


    @classmethod
    def from_rawfile(cls, datafile:str, dataset:str, 
                     in_field:bool=False, mdict:dict=None):
        """
        Load a raw IDG file.

        Parameters:
            datafile (str): The path to the data file.
            dataset (str): The name of the dataset.
            in_field (bool): Whether the data is in-field or not.

        Returns:
            cData (CTDData): The loaded CTDData object.
        """
        # meta dict
        if mdict is None:
            mdict = {}
        mdict['datafile'] = datafile
        mdict['dataset'] = dataset

        # Generate dict
        d, darrays = idg.load_raw(datafile)

        # Init
        pData = cls.from_dict(d, darrays, mdict, dataset, 
                              in_field=in_field)

        return pData


class EMApexData(SoloData):
    """
    Class to hold a full, standard EM Apex
    """
    platform = 'EMApex'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []
