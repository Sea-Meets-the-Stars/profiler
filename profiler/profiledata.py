""" Simple Class to hold glider data """
import os
import glob

import numpy as np
import warnings

from abc import ABCMeta

from scipy.io import loadmat

from cugn import utils as cugn_utils

from IPython import embed

class ProfileData:
    """
    Abstract base class for Gliders

    Attributes:

    dataset (str): The name of the glider data


    """
    __metaclass__ = ABCMeta

    dataset = None
    """
    The name of the glider data
    """

    dtype:str = None
    """
    The type of data
    """

    lat = None
    lon = None
    time = None
    dist = None
    offset = None
    missid = None

    # CTD
    s = None
    t = None
    theta = None
    depth = None

    # ADCP
    has_adcp:bool = False

    def __init__(self, datafile:str, dataset:str):
        self.datafile = datafile
        self.dataset = dataset

    @classmethod
    def from_list(cls, datafiles:list, dataset:str, **kwargs):
        """
        Create a GliderData object from a list of data files.

        Args:
            datafiles (list): A list of data files to load.
            dataset (str): The name of the dataset.

        Returns:
            GliderData: A GliderData object containing the data from the provided files.
        """
        # Hack for the internals
        #profile_arrays = cls.profile_arrays.copy()
        #depth_arrays = cls.depth_arrays.copy()
        #profile_depth_arrays = cls.profile_depth_arrays.copy()

        #def reset_arrays(cls):
        #    cls.profile_arrays = profile_arrays.copy()
        #    cls.depth_arrays = depth_arrays.copy()
        #    cls.profile_depth_arrays = profile_depth_arrays.copy()
        #    return cls

        # Load the first file
        gData = cls(datafiles[0], dataset, **kwargs)

        # Load the rest
        for datafile in datafiles[1:]:
            #embed(header='87 of profiledata')
            #cls = reset_arrays(cls)
            gData2 = cls(datafile, dataset, **kwargs)
            #cls = reset_arrays(cls)
            gData = gData.sum(gData2, **kwargs)

        # Return
        return gData

    def sum(self, other, merge_on_depth:bool=False, **kwargs):
        """
        Add two GliderData objects together.

        Args:
            other (GliderData): The other GliderData object to add.

        Returns:
            GliderData: A new GliderData object containing the combined data.
        """
        # Check the datasets
        if self.dataset != other.dataset:
            raise ValueError("Datasets do not match")

        # Check depths
        if merge_on_depth:
            flg_depth = np.zeros_like(self.depth, dtype=bool)
            oth_idx = []
            for iz, z in enumerate(self.depth):
                mt = np.where(other.depth == z)[0]
                if len(mt) > 0:
                    oth_idx.append(mt[0])
                    flg_depth[iz] = True
            oth_idx = np.array(oth_idx)
        else:
            assert np.allclose(self.depth, other.depth)
            flg_depth = np.ones_like(self.depth, dtype=bool)
            oth_idx = flg_depth

        # Concatenate the data
        gData = self.__class__(self.datafile, self.dataset, **kwargs)
        for key in self.profile_arrays:
            setattr(gData, key, np.concatenate([getattr(self, key), getattr(other, key)]))
        for key in self.profile_depth_arrays:
            setattr(gData, key, np.concatenate(
                [getattr(self, key)[flg_depth], 
                 getattr(other, key)[oth_idx]], 
                axis=1))

        # Return
        return gData
    
    def load_data(self):
        pass

    @property
    def uniq_missions(self):
        """ Return the unique missions """
        return np.unique(self.missid)


    def cut_on_reltime(self, timecut:tuple):
        """
        Cuts the glider data based on good velocity values.

        Variables:
            timecut (tuple): range of times to include 0 to 1

        Returns:
            gData (GliderData): A subset of the original GliderData object containing only the profiles with good velocity values.
        """

        # Relative time
        min_time = self.time.min()
        max_time = self.time.max()

        reltime = (self.time - min_time) / (max_time - min_time)

        # Cut on time
        keep = (reltime > timecut[0]) & (reltime <= timecut[1])

        # Cut
        gData = self.profile_subset(np.where(keep)[0])

        # Return
        return gData

    def profile_subset(self, profiles: np.ndarray, 
                       init:bool=True):
        """
        Create a subset of the GliderData object based on the given profiles.

        Args:
            profiles (np.ndarray): An array of profile indices to include in the subset.

        Returns:
            GliderData: A new GliderData object containing the subset of profiles.
        """
        # Init
        if init:
            gData = self.__class__(self.datafile, self.dataset)
        else:
            gData = self

        # Cut on profiles
        for key in self.profile_arrays:
            setattr(gData, key, getattr(self, key)[profiles])
        for key in self.profile_depth_arrays:
            setattr(gData, key, getattr(self, key)[:, profiles])

        # Return
        return gData

class ADCPData(ProfileData):

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
        ProfileData.__init__(self, datafile, dataset)

    def cut_on_good_velocity(self):
        """
        Cuts the glider data based on good velocity values.

        Returns:
            gData (GliderData): A subset of the original GliderData object containing only the profiles with good velocity values.
        """
        # Cut on velocity
        good = np.isfinite(self.udop) & np.isfinite(self.vdop)
        idx = np.where(good)
        gd_profiles = np.unique(idx[1])

        # Cut
        gData = self.profile_subset(gd_profiles)

        # Return
        return gData