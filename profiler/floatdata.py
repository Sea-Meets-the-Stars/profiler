""" Simple Class to hold glider data """
import os
import glob

import numpy as np

from profiler import profilerdata
from profiler.specific import idg

from IPython import embed

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
