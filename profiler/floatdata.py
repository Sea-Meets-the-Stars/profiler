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

    # Loader
    raw_loader = idg.load_raw

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False):

        # Init
        profilerdata.ProfilerData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.base_key = 'bindata'
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']


class FlipData(profilerdata.ProfilerData):
    """
    Class to hold a full, standard Spray
    """
    platform = 'Flip'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

    # Loader
    raw_loader = idg.load_raw

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False):

        # Init from the parent
        profilerdata.ProfilerData.__init__(self, datafile, dataset)
        self.in_field = in_field
        self.base_key = 'bindata'
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't', 'theta', 'sigma']




class EMApexData(SoloData):
    """
    Class to hold a full, standard EM Apex
    """
    platform = 'EMApex'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

class AltoData(SoloData):
    """
    Class to hold a full, standard EM Apex
    """
    platform = 'Alto'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []