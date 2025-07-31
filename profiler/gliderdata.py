""" Simple Class to hold glider data """

from profiler import profilerdata

from IPython import embed

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