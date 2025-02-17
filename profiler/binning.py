import numpy as np
from datetime import datetime
import time

def binsolo(data, pmin, pstep, pmax, pd, exclude='bad', useraw=False):
    """
    Bins oceanographic data in pressure or depth on the grid [pmin:pstep:pmax].
    
    Parameters:
    -----------
    data : dict
        Dictionary containing oceanographic data with fields like time, lat, lon, etc.
    pmin : float
        Minimum pressure/depth value
    pstep : float
        Step size for pressure/depth bins
    pmax : float
        Maximum pressure/depth value
    pd : str
        'p' for pressure or 'd' for depth binning
    exclude : str, optional
        'none', 'bad', or 'questionable' to specify which points to exclude
    useraw : bool, optional
        If True, use raw data fields (praw, sraw, etc.)
    
    Returns:
    --------
    bindata : dict
        Dictionary containing binned data
    """
    
    # Define flags
    CTD_SENSOR_OFF = 9
    CTD_BAD = 7
    CTD_QUESTIONABLE = 3
    GPS_GOOD = 0
    
    # Initialize bindata dictionary
    bindata = {
        'time': data['time'][:, 1],
        'lat': data['lat'][:, 1],
        'lon': data['lon'][:, 1],
        'u': data['u'],
        'v': data['v'],
        'tsurf': data['tsurf'],
        'usurf': data['usurf'],
        'vsurf': data['vsurf']
    }
    
    # Set up pressure/depth grid
    if pd == 'p':
        bindata['p'] = np.arange(pmin, pmax + pstep, pstep)
        pstr = 'p'
    elif pd == 'd':
        bindata['depth'] = np.arange(pmin, pmax + pstep, pstep)
        pstr = 'depth'
    else:
        raise ValueError("pd must be 'p' (pressure) or 'd' (depth)")
    
    # Set up raw/processed data string
    pstrdata = f"{pstr}raw" if useraw else pstr
    
    # Set maximum flag based on exclude parameter
    if exclude.startswith('n'):
        maxflag = CTD_SENSOR_OFF
    elif exclude.startswith('b'):
        maxflag = CTD_BAD
    elif exclude.startswith('q'):
        maxflag = CTD_QUESTIONABLE
    else:
        raise ValueError("exclude must be 'none', 'bad' or 'questionable'")
    
    # Initialize arrays for binned data
    np_bins = len(bindata[pstr])
    nt = len(bindata['time'])
    for field in ['t', 's', 'theta', 'sigma', 'rho']:
        bindata[field] = np.full((np_bins, nt), np.nan)
    
    # Bin the data
    for n in range(nt):
        if data[pstrdata][n] is not None and len(data[pstrdata][n]) > 0:
            ibin = np.round((data[pstrdata][n] - pmin) / pstep).astype(int)
            
            for m in range(np_bins):
                try:
                    # Temperature
                    qual_field = 'traw' if useraw else 't'
                    data_field = 'traw' if useraw else 't'
                    iit = (ibin == m) & (data['qual'][qual_field][n] < maxflag)
                    if np.any(iit):
                        bindata['t'][m, n] = np.nanmean(data[data_field][n][iit])
                except Exception as err:
                    print(f"t {'raw' if useraw else 'bin'} index = [{m}, {n}]: {str(err)}")
                
                try:
                    # Salinity and derived variables
                    qual_field = 'sraw' if useraw else 's'
                    data_field = 'sraw' if useraw else 's'
                    iis = (ibin == m) & (data['qual'][qual_field][n] < maxflag)
                    ii = iit & iis
                    
                    if np.any(iis):
                        bindata['s'][m, n] = np.nanmean(data[data_field][n][iis])
                    if np.any(ii):
                        for field in ['theta', 'sigma', 'rho']:
                            field_raw = f"{field}raw" if useraw else field
                            bindata[field][m, n] = np.nanmean(data[field_raw][n][ii])
                except Exception as err:
                    print(f"binsolo: s {'raw' if useraw else 'bin'} index = [{m}, {n}]: {str(err)}")
    
    # Add creation time
    bindata['bintime'] = int(time.time())
    
    return bindata