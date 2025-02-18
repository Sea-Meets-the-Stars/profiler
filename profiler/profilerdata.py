""" Simple Class to hold data from a Profiler"""

import numpy as np
import warnings

from abc import ABCMeta

import pandas

from IPython import embed

class ProfilerData:
    """
    Abstract base class for Profilers

    Attributes:

    dataset (str): The name of the glider data


    """
    __metaclass__ = ABCMeta


    # Max dimension for z/p (just to keep track of the arrays)
    Ndepth:int = None

    # Standard variables
    lat = None
    lon = None
    time = None

    # glider offset
    dist = None
    offset = None

    # Meta
    missid:str = None
    platform:str = None
    pi:str = None  # Principal Invesitgator
    pdict:dict = None # dict on the profiler
    dataset = None  # The name of the dataset
    datafile:str = None

    # CTD -- Nprof, Ndepth
    s = None
    t = None
    p = None
    theta = None
    depth = None
    qual:dict = None

    # ADCP
    has_adcp:bool = False

    def __init__(self, datafile:str, dataset:str):
        self.datafile = datafile
        self.dataset = dataset

    def load_data(self):
        pass

    @classmethod
    def from_dict(cls, d:dict, darrays:dict, mdict:dict,
                  dataset:str, in_field:bool=False):
        """
        Create a ProfilerData object from a dictionary of data.

        Args:
            d (dict): A dictionary of data.
            dataset (str): The name of the dataset.
            darrrays (dict): A dictionary of data arrays.
                Required keys are:
                    profile_arrays (list): A list of profile arrays.
                    depth_arrays (list): A list of depth arrays.
                    profile_depth_arrays (list): A list of profile + depth arrays.
                    scalar_keys (list): A list of scalar keys.
            mdict (dict): A dictionary of metadata.
            in_field (bool): Whether the data is from the infield processing.

        Returns:
            ProfilerData: A ProfilerData object containing the data from the dictionary.
        """
        # Init
        pData = cls.__new__(cls)
        pData.dataset = dataset
        pData.in_field = in_field

        # Meta dict
        for key in mdict.keys():
            setattr(pData, key, mdict[key])

        # Data arrays
        for key in darrays.keys():
            setattr(pData, key, darrays[key])

        # Scalars
        for key in pData.scalar_keys:
            setattr(pData, key, d[key])

        # Depth arrays
        for key in pData.depth_arrays:
            setattr(pData, key, d[key])

        # Profile arrays
        for key in pData.profile_arrays:
            setattr(pData, key, d[key])

        # Profile + depth
        for key in pData.profile_depth_arrays:
            setattr(pData, key, d[key])

        # Return
        return pData

    @property
    def ptime(self):  # pandas time
        return pandas.to_datetime(self.time, unit='s')

    @property
    def Nprof(self):
        return len(self.time)

    def cut_on_reltime(self, timecut:tuple):
        """
        Cuts the profiler data based on good velocity values.

        Variables:
            timecut (tuple): range of times to include 0 to 1

        Returns:
            pData (ProfilerData): A subset of the original ProfilerData object containing only the profiles with good velocity values.
        """

        # Relative time
        min_time = self.time.min()
        max_time = self.time.max()

        reltime = (self.time - min_time) / (max_time - min_time)

        # Cut on time
        keep = (reltime > timecut[0]) & (reltime <= timecut[1])

        # Cut
        pData = self.profile_subset(np.where(keep)[0])

        # Return
        return pData

    def profile_subset(self, profiles: np.ndarray, 
                       init:bool=True):
        """
        Create a subset of the ProfilerData object based on the given profiles.

        Args:
            profiles (np.ndarray): An array of profile indices to include in the subset.

        Returns:
            GliderData: A new ProfilerData object containing the subset of profiles.
        """
        # Init
        if init:
            pData = self.__class__(self.datafile, self.dataset)
        else:
            pData = self

        # Cut on profiles
        for key in self.profile_arrays:
            setattr(pData, key, getattr(self, key)[profiles])
        for key in self.profile_depth_arrays:
            setattr(pData, key, getattr(self, key)[:, profiles])

        # Return
        return pData

    def rstr_meta(self):
        """ Return the representation of the CTDData object """
        rstr_meta = []
        rstr_meta += [f"{self.__class__.__name__} object for {self.dataset}\n"]
        rstr_meta += [f"  Number of profiles: {self.Nprof}\n"]
        rstr_meta += [f"  Time range: {self.ptime.min()} to {self.ptime.max()}\n"]

        return rstr_meta

    def rstr_settings(self):
        """ Return the representation of the CTDData object """
        # Settings (adcp_on, in_field)
        rstr_settings = []
        return rstr_settings

    def rstr_variables(self):
        # Variables
        rstr_var = []
        rstr_var += ["  Variables:\n"]
        for key in self.depth_arrays:
            rstr_var += [f"    {key}: {getattr(self, key).shape}\n"]
        for key in self.profile_arrays:
            rstr_var += [f"    {key}: {getattr(self, key).shape}\n"]
        for key in self.profile_depth_arrays:
            rstr_var += [f"    {key}: {getattr(self, key).shape}\n"]
        #
        return rstr_var

    # Combine
    def __repr__(self):

        # Grab em
        r_m = self.rstr_meta()
        r_s = self.rstr_settings()
        r_v = self.rstr_variables()

        # Combine
        all_r = r_m + r_s + r_v
        rstr = ''.join(all_r)

        # Return
        return rstr


class ADCPData(ProfilerData):

    """
    Class to hold CTD data 
    """
    __metaclass__ = ABCMeta

    # ADCP
    udop = None 
    vdop = None
    udopacross = None
    udopalong = None

    has_adcp = True
    adcp_on:bool = None

    def __init__(self, datafile:str, dataset:str, adcp_on:bool=True):
        
        # Init
        self.adcp_on = adcp_on
        ProfilerData.__init__(self, datafile, dataset)

    def cut_on_good_velocity(self):
        """
        Cuts the glider data based on good velocity values.

        Returns:
            pData (ProfilerData): A subset of the original ProfilerData object containing 
            only the profiles with good velocity values.
        """
        # Cut on velocity
        good = np.isfinite(self.udop) & np.isfinite(self.vdop)
        idx = np.where(good)
        gd_profiles = np.unique(idx[1])

        # Cut
        gData = self.profile_subset(gd_profiles)

        # Return
        return gData