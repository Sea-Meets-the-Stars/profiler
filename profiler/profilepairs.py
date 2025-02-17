""" Simple Class to Analyze Pairs of Profilers """

import numpy as np
import datetime
import getpass

from scipy.interpolate import interp1d

import pandas

from cugn import utils as cugn_utils

from IPython import embed

def load_Sndict(filename:str):
    """
    Load Sn_dict from a JSON file.

    Parameters:
        filename (str): The path to the JSON file.

    Returns:
        dict: The loaded Sn_dict.
    """

    Sn_dict = cugn_utils.loadjson(filename)
    # Convert lists to numpy arrays
    for key in Sn_dict.keys():
        if isinstance(Sn_dict[key], list):
            Sn_dict[key] = np.array(Sn_dict[key])

    # Return
    return Sn_dict

class ProfilerPairs:

    pdata:list = None
    """
    List of profiledata.ProfileData objects
    """

    idx0:np.ndarray = None
    """ 
    Index array for the first glider of the pair
    """

    idx1:np.ndarray = None
    """ 
    Index array for the second glider of the pair
    """

    dtime:np.ndarray = None
    """
    Time difference between the two gliders [hours]
    """

    iz:int = None
    """
    Index of the vertical level
    """

    def __init__(self, pdata:list, 
                 max_dist:float=None, max_time:float=None,
                 from_scratch:bool=True, avoid_same_glider:bool=True):
        """ Object to generate and hold pairs of 
        measurements from profilers

        Args:
            pdata (list): List of profiledata.ProfileData objects
            max_dist (float, optional): Maximum distance between gliders. Defaults to None.
        """

        # Inputs
        self.pdata = pdata
        self.max_dist = max_dist
        self.max_time = max_time
        self.avoid_same_glider = avoid_same_glider

        # Separations
        self.r = None
        self.rx = None
        self.ry = None
        self.rxN = None
        self.ryN = None

        # Velocity
        self.umag = None
        self.du = None
        self.dv = None
        self.duL = None
        self.duT = None

        # Other variables
        self.dS = None
        self.dT = None

        self.generate_pairs(max_dist=max_dist, max_time=max_time,
                            from_scratch=from_scratch,
                            avoid_same_glider=avoid_same_glider)

    @property
    def npairs(self):
        if self.idx0 is not None:
            return self.idx0.size
        else:
            return 0

    def add_meta(self, sdict:dict):
        """
        Add metadata to the GliderPairs object.

        Args:
            sdict (dict): A dictionary containing analysis output
        """
        sdict['config']['max_dist'] = self.max_dist
        sdict['config']['max_time'] = self.max_time
        sdict['config']['avoid_self'] = self.avoid_same_glider
        sdict['config']['datasets'] = [item.dataset for item in self.pdata]
        if self.iz is not None:
            sdict['config']['iz'] = self.iz
        # Add creation date
        sdict['config']['creation_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Add created by
        sdict['config']['created_by'] = getpass.getuser()

    def generate_pairs(self, max_dist:float=None, max_time:float=None,
                       from_scratch:bool=True, avoid_same_glider:bool=True):
        """
        Generate pairs of gliders that are within max_dist and max_time.

        Args:
            max_dist (float, optional): Maximum distance between gliders. Defaults to None.
            max_time (float, optional): Maximum time difference between gliders. Defaults to None.
            from_scratch (bool, optional): Whether to generate pairs from scratch. Defaults to True.
            avoid_same_glider (bool, optional): Whether to avoid pairing the same glider with itself. Defaults to True.

        Raises:
            ValueError: If neither max_dist nor max_time is specified.
            ValueError: If from_scratch is set to False.

        Notes:
            - If max_dist is not specified, only time-based pairing will be performed.
            - If max_time is not specified, only distance-based pairing will be performed.
        """
        if max_dist is None and max_time is None:
            raise ValueError("Must specify either max_dist or max_time")

        if not from_scratch:
            raise ValueError("Only from_scratch=True is supported")

        # Concatenate the various profilers

        # Time
        if max_time is not None:
            # Times
            t = np.concatenate([item.time for item in self.pdata])
            dt = np.zeros((t.size, t.size))
            for kk in range(t.size):
                dt[kk] = (t[kk] - t)/3600.  # hours

            # Insert a negative sign (trust me)
            dt = -1.*dt

            # Restrcit to the positive values to avoid double counting
            pos = dt > 0.
            tcut = dt < max_time

            cut = tcut & pos
            idx = np.where(tcut & pos)
            # Parse
            self.idx0 = idx[0]
            self.idx1 = idx[1]

        # Avoid using the same glider for any pairs
        if avoid_same_glider:
            keep = self.data('missid', 0) != self.data('missid', 1)
            # Parse
            self.idx0 = self.idx0[keep]
            self.idx1 = self.idx1[keep]

        # Calculate standard stats
        self.update()

        # Checks
        if avoid_same_glider:
            assert not np.any(self.data('missid', 0) == self.data('missid', 1))

    def data(self, key:str, ipair:int, iz:int=None):
        """
        Retrieve data from the profilers

        Parameters:
            key (str): The key of the data to retrieve.
            ipair (int): The index of the pair.
                0: First glider
                1: Second glider
                2: Both gliders
            iz (int, optional): The index of the depth level. Defaults to None.

        Returns:
            ndarray: The retrieved data.

        Raises:
            ValueError: If ipair is not 0, 1, or 2.
        """
        # Build up the data array from the pdata list
        if iz is None or iz >= 0:
            if getattr(self.pdata[0], key).ndim >= 2:
                # Find the minimum number of levels
                minl = np.min([getattr(item, key).shape[0] for item in self.pdata])
                # Concatenate
                data = np.concatenate([getattr(item, key)[:minl,...] for item in self.pdata], axis=1)
            else:
                data = np.concatenate([getattr(item, key) for item in self.pdata])


        if ipair == 2:
            idx = np.unique(np.concatenate((self.idx0, self.idx1)))
        elif ipair in [0,1]:
            idx = self.idx0 if ipair == 0 else self.idx1
        else:
            raise ValueError("Bad ipair")
        # Return
        if iz is None:
            return data[idx]
        else:
            if iz >=0 :
                return data[iz][idx]
            else: # isopycnals
                vals = []
                for interpolator in self.interpolators:
                    if interpolator is None:
                        vals.append(np.nan)
                    else:
                        vals.append(interpolator(self.sigma))
                # 
                return np.array(vals)[idx]
        
    def update(self):
        """
        Update the glider pairs.

        This method calculates the separation between two gliders, generates the r vector,
        and calculates the time difference between the two gliders.

        Parameters:
            None

        """
        # Separations
        d0 = self.data('dist', 0)
        d1 = self.data('dist', 1)
        #
        o0 = self.data('offset', 0)
        o1 = self.data('offset', 1)

        # Separation
        self.r = np.sqrt((d0-d1)**2 + (o0-o1)**2)

        # Generate the r vector
        self.rx = d1-d0
        self.ry = o1-o0
        self.rxN = (d1-d0)/self.r
        self.ryN = (o1-o0)/self.r

        # Time
        t0 = self.data('time', 0)
        t1 = self.data('time', 1)
        self.dtime = (t1-t0)/3600.

    def prep_isopycnals(self, key:str):
        """ 
        Generate density interpolators for all of the profiles
        """

        self.interpolators = []
        for pdata in self.pdata:
            sigma0 = getattr(pdata, 'sigma')
            data = getattr(pdata, key)
            # Loop on porfiles
            ok = np.isfinite(sigma0) & np.isfinite(data)
            for profile in range(sigma0.shape[1]):
                # Interpolators
                if np.sum(ok[:,profile]) < 2:
                    self.interpolators.append(None)
                    continue
                # Do it
                f = interp1d(sigma0[:,profile][ok[:,profile]], 
                             data[:,profile][ok[:,profile]],
                             kind='linear', bounds_error=False)
                self.interpolators.append(f)

    def calc_delta(self, iz, variables:str,
                   skip_velocity:bool=False):

        # Depth?
        if iz >= 0:
            self.iz = iz
        else:  # isopycnal
            self.sigma = np.abs(iz)

        # Velocity
        if not skip_velocity:
            u0 = self.data('udopacross', 0, iz)
            u1 = self.data('udopacross', 1, iz)
            v0 = self.data('udopalong', 0, iz)
            v1 = self.data('udopalong', 1, iz)

            self.umag = np.sqrt((u1-u0)**2 + (v1-v0)**2)
            self.du = u1-u0
            self.dv = v1-v0

            self.duL = self.rxN*self.du + self.ryN*self.dv
            self.duT = self.ryN*self.du + self.rxN*self.dv

        # Other
        if 'dS' in variables:
            s0 = self.data('s', 0, iz)
            s1 = self.data('s', 1, iz)
            self.dS = s1-s0

        # Other
        if 'dT' in variables:
            t0 = self.data('t', 0, iz)
            t1 = self.data('t', 1, iz)
            self.dT = t1-t0


    def calc_Sn(self, variables:str):

        self.variables = variables
        # duL
        if variables == 'duLduLduL':
            self.S1 = self.duL
            self.S2 = self.duL**2
            self.S3 = self.duL**3
            self.dlbls = ['duL', 'duL**2', variables]
        elif variables == 'duTduTduT':
            self.S1 = self.duT
            self.S2 = self.duT**2
            self.S3 = self.duT**3
            self.dlbls = ['duT', 'duT**2', variables]
        elif variables == 'duLTduLTduLT':
            self.S1 = self.duL + self.duT
            self.S2 = self.duL**2 + self.duT**2
            self.S3 = self.duL*(self.S2)
            self.dlbls = ['duLT', 'duLT**2', variables]
        elif variables == 'duLdSdS':
            self.S1 = self.duL
            self.S2 = self.dS**2
            self.S3 = self.duL*self.dS*self.dS
            self.dlbls = ['duL', 'dS**2', variables]
        elif variables == 'duLdTdT':
            self.S1 = self.duL
            self.S2 = self.dT**2
            self.S3 = self.duL*self.dT*self.dT
            self.dlbls = ['duL', 'dT**2', variables]
        elif variables == 'duLduTduT':
            self.S1 = self.duL
            self.S2 = self.duT**2
            self.S3 = self.duL*self.duT*self.duT
            self.dlbls = ['duL', 'duT**2', variables]
        elif variables == 'dTdTdT':
            self.S1 = self.dT
            self.S2 = self.dT**2
            self.S3 = self.dT**3
            self.dlbls = ['dT', 'dT**2', variables]
        else: 
            raise ValueError("Bad variables")

    def calc_Sn_vs_r(self, rbins:np.ndarray, nboot:int=None):
        """
        Calculate S1, S2, S3 vs r in bins.

        Parameters:
            rbins (np.ndarray): Bin edges

        Returns:
            np.ndarray: Binned S3 values
        """
        N = []
        avg_S1 = []
        med_S1 = []
        std_S1 = []
        err_S1 = []
        avg_S2 = []
        std_S2 = []
        err_S2 = []
        avg_S3 = []
        std_S3 = []
        err_S3 = []

        avg_r = []
        for ss in range(rbins.size-1):
            in_r = (self.r > rbins[ss]) & (self.r <= rbins[ss+1])
            #
            N.append(np.sum(in_r))

            # Bootstrap?
            if nboot is not None:
                # Bootstrap samples
                r_idx = np.where(in_r)[0]
                in_r = np.random.choice(
                    r_idx, size=(nboot,N[-1]), replace=True)
            
            # Stats
            avg_r.append(np.nanmean(self.r[in_r]))
            avg_S1.append(np.nanmean(self.S1[in_r])) 
            med_S1.append(np.nanmedian(self.S1[in_r])) 
            std_S1.append(np.nanstd(self.S1[in_r])) 
            avg_S2.append(np.nanmean(self.S2[in_r])) 
            std_S2.append(np.nanstd(self.S2[in_r])) 
            avg_S3.append(np.nanmean(self.S3[in_r])) 
            std_S3.append(np.nanstd(self.S3[in_r])) 

            if nboot is not None:
                err_S1.append(np.nanstd(np.nanmean(self.S1[in_r], axis=1)))
                err_S2.append(np.nanstd(np.nanmean(self.S2[in_r], axis=1)))
                err_S3.append(np.nanstd(np.nanmean(self.S3[in_r], axis=1)))
                #embed(header='calc_Sn_vs_r 223')
            else:
                err_S1.append(np.nanstd(self.S1[in_r])/np.sqrt(np.sum(np.isfinite(self.S1[in_r])))) 
                err_S2.append(np.nanstd(self.S2[in_r])/np.sqrt(np.sum(np.isfinite(self.S2[in_r])))) 
                err_S3.append(np.nanstd(self.S3[in_r])/np.sqrt(np.sum(np.isfinite(self.S3[in_r])))) 

        # generate a dict
        out_dict = {}
        out_dict['config'] = {}
        out_dict['config']['variables'] = self.variables 
        out_dict['config']['N'] = np.array(N)
        out_dict['r'] = np.array(avg_r)

        out_dict['S1_'+f'{self.dlbls[0]}'] = np.array(avg_S1)
        out_dict['std_S1_'+f'{self.dlbls[0]}'] = np.array(std_S1)
        out_dict['med_S1_'+f'{self.dlbls[0]}'] = np.array(med_S1)
        out_dict['err_S1_'+f'{self.dlbls[0]}'] = np.array(err_S1)
        out_dict['S2_'+f'{self.dlbls[1]}'] = np.array(avg_S2)
        out_dict['std_S2_'+f'{self.dlbls[1]}'] = np.array(std_S2)
        out_dict['err_S2_'+f'{self.dlbls[1]}'] = np.array(err_S2)
        out_dict['S3_'+f'{self.dlbls[2]}'] = np.array(avg_S3)
        out_dict['std_S3_'+f'{self.dlbls[2]}'] = np.array(std_S3)
        out_dict['err_S3_'+f'{self.dlbls[2]}'] = np.array(err_S3)

        # Return
        return out_dict

    def calc_corr_Sn(self, Sn_dict:dict):
        """
        Calculate the corrected values of S2 and S3 in the given Sn_dict.

        Parameters:
            Sn_dict (dict): A dictionary containing the values of S1, S2, S3, and r.

        """

        # Init
        Sn_dict['S2corr_'+f'{self.dlbls[1]}'] = Sn_dict['S2_'+f'{self.dlbls[1]}'].copy()
        Sn_dict['S3corr_'+f'{self.dlbls[2]}'] = Sn_dict['S3_'+f'{self.dlbls[2]}'].copy()

        # Correct me
        for ibin in range(Sn_dict['r'].size):
            Sn_dict['S2corr_'+f'{self.dlbls[1]}'][ibin] -= Sn_dict['S1_'+f'{self.dlbls[0]}'][ibin]**2
            Sn_dict['S3corr_'+f'{self.dlbls[2]}'][ibin] -= 3.*Sn_dict['S1_'+f'{self.dlbls[0]}'][ibin]*Sn_dict['S2_'+f'{self.dlbls[1]}'][ibin] \
                + 2.*Sn_dict['S1_'+f'{self.dlbls[0]}'][ibin]**3


    def __repr__(self):
        """ Return the representation of the CTDData object """
        rstr = f"ProfilerPair object for the following datasets:\n"
        for item in self.pdata:
            rstr += f" {item.dataset}, {item.__class__.__name__}\n"
        rstr += f"  Number of pairs: {self.npairs}\n"
        t = pandas.to_datetime(np.concatenate([item.time for item in self.pdata]), unit='s')
        rstr += f"  Time range: {t.min()} to {t.max()}\n"
        # Variables
        #rstr += "  Variables:\n"
        #for key in self.depth_arrays:
        #    rstr += f"    {key}: {getattr(self, key).shape}\n"
        #for key in self.profile_arrays:
        #    rstr += f"    {key}: {getattr(self, key).shape}\n"
        #for key in self.profile_depth_arrays:
        #    rstr += f"    {key}: {getattr(self, key).shape}\n"
        return rstr
