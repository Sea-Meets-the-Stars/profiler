""" Simple Class to hold Triaxus data """
import os
import glob

import numpy as np

from profiler import profilerdata
from profiler.specific import idg 

from IPython import embed

class TriaxusData(profilerdata.ADCPData):
    """
    Class to hold a standard Triaxus dataset
    """
    platform = 'Triaxus'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False, binned:bool=False):

        # Init
        profilerdata.ADCPData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.base_key = 'bindata'
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'sigma']

        self.adcp_on = False

