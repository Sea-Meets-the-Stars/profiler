""" Simple Class to hold glider data """

import numpy as np

from profiler import profilerdata

from IPython import embed

# Meter-to-degree conversion (equatorial approximation)
_M_PER_DEG = 111_120.0 # Matches calc_dist_offset()

class SprayData(profilerdata.ADCPData):
    """
    Class to hold a full, standard Spray
    """
    dtype = 'Spray'

    in_field:bool = None
    base_key:str = None

    scalar_keys:list = []

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False):

        # Init
        # Existing arrays
        self.profile_arrays = ['time', 'lat', 'lon']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't']#, 'theta', 'sigma']

        self.in_field = in_field
        if not self.in_field:
            self.adcp_on:bool=True
            #

        # Init
        profilerdata.ADCPData.__init__(self, datafile, dataset)


    @classmethod
    def from_QG_glider(cls, glider_df, meta, missid):
        """Build a SprayData instance from QG-sampled glider velocities.

        Unlike DrifterData.from_QG_trajectory(), this uses the pre-sampled
        u_qg, v_qg columns directly — no finite differencing.

        Parameters
        ----------
        glider_df : pd.DataFrame
            Glider velocity output with columns:
            x, y, time, missid, x_m, y_m, u_qg, v_qg
        meta : dict
            Metadata dict (must contain 'dx', 'nx').
        missid : int
            Glider mission ID to extract.

        Returns
        -------
        SprayData
        """
        # Extract this glider's rows, sorted by time
        sub = glider_df[glider_df.missid == missid].sort_values('time')
        x_m = sub.x_m.values
        y_m = sub.y_m.values
        times = sub.time.values.astype(float)
        u = sub.u_qg.values
        v = sub.v_qg.values

        # Build the SprayData object (bypass __init__ which needs a datafile)
        obj = cls.__new__(cls)
        obj.datafile = None
        obj.dataset = f'QG_glider_{int(missid)}'
        obj.in_field = False
        obj.has_adcp = True
        obj.adcp_on = True

        # Array layout declarations
        obj.profile_arrays = ['time', 'lat', 'lon']
        obj.depth_arrays = ['depth']
        obj.profile_depth_arrays = ['udop', 'vdop']
        obj.scalar_keys = []
        obj.meta_keys = ['missid', 'platform', 'dataset']

        # Profile arrays — one element per time step
        # Add a tiny per-glider offset so ProfilerPairs dt>0 filter works
        obj.time = times + missid * 1e-3
        obj.lat = y_m / _M_PER_DEG
        obj.lon = x_m / _M_PER_DEG

        # Depth array — single surface level
        obj.depth = np.array([0.0])

        # Velocity arrays — shape (Ntime, 1) for the single depth level
        # Use sampled QG velocities directly (no finite differencing)
        obj.udop = u[:, np.newaxis]
        obj.vdop = v[:, np.newaxis]

        # Mission ID (used for avoid_same_glider in ProfilerPairs)
        obj.missid = int(missid)

        return obj

    @classmethod
    def all_from_QG_glider(cls, glider_df, meta):
        """Build a list of SprayData objects, one per glider mission ID.

        Parameters
        ----------
        glider_df : pd.DataFrame
            Glider velocity output (all gliders).
        meta : dict
            Metadata dict.

        Returns
        -------
        list of SprayData
        """
        ids = sorted(glider_df.missid.unique())
        return [cls.from_QG_glider(glider_df, meta, mid) for mid in ids]

    def rstr_settings(self):
        """ Return the representation of the CTDData object """
        # Settings (adcp_on, in_field)
        r_s = super().rstr_settings()

        # More settings
        r_s.append(f"  In field? {self.in_field}")
        r_s.append(f"  ADCP on? {self.adcp_on}")

        return r_s


class SlocumData(profilerdata.ProfilerData):
    """
    Class to hold a full, standard Slowcum glider
    """
    platform = 'Slocum'

    in_field:bool = None

    scalar_keys:list = []
    
    # Loader
    loader_dict = dict(t='temperature', s='salinity')

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False, binned:bool=False):

        # Init
        profilerdata.ProfilerData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't']#, 'SA']

class SeagliderData(profilerdata.ADCPData):
    """
    Class to hold a full, standard Seaglider glider
    """
    platform = 'Seaglider'

    in_field:bool = None

    scalar_keys:list = []
    
    # Loader
    loader_dict = dict(t='T', s='S')

    def __init__(self, datafile:str, dataset:str,
                    in_field:bool=False, binned:bool=False):

        # Init
        profilerdata.ProfilerData.__init__(self, datafile, dataset)

        self.in_field = in_field
        self.profile_arrays = ['lat', 'lon', 'time']
        self.depth_arrays = ['depth']
        self.profile_depth_arrays = ['s', 't']

        if not self.in_field:
            self.adcp_on:bool=True