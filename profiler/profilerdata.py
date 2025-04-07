""" Simple Class to hold data from a Profiler"""

import numpy as np
import warnings

from abc import ABCMeta, abstractmethod

import pandas

from profiler.loading import binned
from profiler import io as p_io

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
    data_keys:list = []

    # Meta
    missid:int = None
    platform:str = None
    pi:str = None  # Principal Invesitgator
    pdict:dict = None # dict on the profiler
    dataset = None  # The name of the dataset
    meta_keys:list = []

    # I/O
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

    @classmethod
    def from_binned_file(cls, datafile:str, bin_style:str,
                  dataset:str, in_field:bool=False, 
                  missid:int=None, extra_dict:dict=None):

        # Init
        pData = cls(datafile, dataset)
        pData.datafile = datafile
        pData.dataset = dataset
        pData.in_field = in_field

        if extra_dict is not None:
            for key in extra_dict:
                setattr(pData, key, extra_dict[key])

        # Load
        binned.load(pData, bin_style, in_missid=missid)

        return pData

    @abstractmethod
    def raw_loader(self, datafile:str):
        pass

    @classmethod
    def from_rawfile(cls, datafile:str, dataset:str, 
                     in_field:bool=False, mdict:dict=None,
                     **kwargs):
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
        d, darrays = cls.raw_loader(datafile)

        # Init
        pData = cls.from_dict(d, darrays, mdict, dataset, 
                              in_field=in_field)

        return pData

    @classmethod
    def from_dict(cls, d:dict, darrays:dict, mdict:dict,
                  dataset:str, in_field:bool=False):
        """
        Create a ProfilerData object from a dictionary of data.

        Args:
            d (dict): A dictionary of data.
                Required fields:
                    time (np.ndarray): An array of times.
                    lat (np.ndarray): An array of latitudes.
                    lon (np.ndarray): An array of longitudes.
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
        pData.meta_keys = list(mdict.keys())

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
    def raw_loader(self):
        pass

    @property
    def ptime(self):  # pandas time
        return pandas.to_datetime(self.time, unit='s')

    @property
    def Nprof(self):
        return len(self.time)

    @property
    def darrays(self):
        darrays = {}
        for key in ['profile_arrays', 'depth_arrays', 
                    'profile_depth_arrays', 'scalar_keys']:
            darrays[key] = getattr(self, key)
        return darrays

    @property
    def meta_dict(self):
        mdict = {}
        for attr in self.meta_keys: #['missid', 'platform', 'pi', 'pdict', 'dataset', 'datafile']:
            if hasattr(self, attr):
                mdict[attr] = getattr(self, attr)
        return mdict

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
        rstr_meta += [f"  Mission ID: {self.missid}\n"]
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

    def to_dict(self):
        out_dict = {}

        # Meta
        for key in self.meta_keys:
            out_dict[key] = getattr(self, key)

        # Data
        for key in self.data_keys:
            out_dict[key] = getattr(self, key)

        # Scalars
        for key in self.scalar_keys:
            out_dict[key] = getattr(self, key)

        # Arrays
        for karray in [self.depth_arrays,
                      self.profile_arrays, 
                      self.profile_depth_arrays]:
            for key in karray:
                out_dict[key] = getattr(self, key)

        # Key me
        for keys in ['meta_keys', 'data_keys', 'scalar_keys']:
            out_dict[keys] = getattr(self, keys)

        return out_dict

    def write(self, outfile:str, gzip:bool=False):
        # dict me
        odict = self.to_dict()
        # JSON
        jdict = p_io.jsonify(odict)
        # Write`
        p_io.savejson(outfile, jdict, overwrite=True)
        # gzip?
        if gzip:
            outfile += '.gz'
            raise NotImplementedError("Ooops")
        # done
        print(f'Wrote: {outfile}')

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