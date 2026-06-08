""" Simple Class to hold VMP data """
import os
import glob

import numpy as np

from profiler import profilerdata
from profiler.specific import idg 

from IPython import embed

class VMPData(profilerdata.ProfilerData):
    """
    Class to hold a standard VMP dataset
    """
    platform = 'VMP'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False, binned:bool=False):

        # Init
        profilerdata.ProfilerData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.base_key = 'bindata'
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'theta', 'sigma', 'rho']

