import numpy as np
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from profiler.profilerdata import ProfilerData

from IPython import embed

def bin_profilerdata(pdata:"ProfilerData", 
                     pmin:float=10, pstep:float=10, 
                     pmax:float=200., pd:str='d', 
                     exclude='bad', add_vel:bool=True):
    """
    Bins oceanographic data in pressure or depth on the grid [pmin:pstep:pmax].
    
    Parameters:
    -----------
    pdata : profilerdata.ProfilerData
        Object containing oceanographic data with fields like time, lat, lon, etc.
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
        'time': pdata.time,
        'lat': pdata.lat,
        'lon': pdata.lon,
    }

    '''
    if add_vel:
        bindata.update({
        'u': data['u'],
        'v': data['v'],
        'tsurf': data['tsurf'],
        'usurf': data['usurf'],
        'vsurf': data['vsurf']})
    '''
    
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
    pstrdata = pstr
    
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
        bindata[field] = np.full((nt, np_bins), np.nan)
    
    # Bin the data
    for n in range(nt):  # Loop on profiles
        vals = getattr(pdata, pstrdata)[n]
        #if vals is not None and len(vals) > 0: # THIS CHECK WAS SUPERFLOUX
        ibin = np.round((vals - pmin) / pstep)
        # NaNs
        ibin[np.isnan(ibin)] = -999999
        ibin = ibin.astype(int)

        # Loop on bins
        for m in range(np_bins):
            try:
                # Temperature
                #qual_field = 't'
                #data_field = 't'
                qualvals = getattr(pdata, 'qual')['t'][n]

                iit = (ibin == m) & (qualvals < maxflag)
                if np.any(iit):
                    bindata['t'][n,m] = np.nanmean(
                        pdata.t[n][iit])
            except Exception as err:
                print(f"t {'bin'} index = [{m}, {n}]: {str(err)}")
                embed(header='111 of binning')
            
            try:
                # Salinity and derived variables
                #qual_field = 's'
                #data_field = 's'
                qualvals = getattr(pdata, 'qual')['s'][n]
                iis = (ibin == m) & (qualvals < maxflag)
                ii = iit & iis
                
                if np.any(iis):
                    bindata['s'][n,m] = np.nanmean(pdata.s[n][iis])
                if np.any(ii):
                    for field in ['theta', 'sigma', 'rho']:
                        vals = getattr(pdata, field)[n]
                        bindata[field][n,m] = np.nanmean(vals[ii])
            except Exception as err:
                print(f"binsolo: s {'bin'} index = [{m}, {n}]: {str(err)}")
    
    # Add creation time
    #bindata['bintime'] = int(time.time())

    # Create a new class for the binned data
    #darrays = {}
    #for key in ['profile_arrays', 'depth_arrays', 
    #            'profile_depth_arrays', 'scalar_keys']:
    #    darrays[key] = getattr(pdata, key)

    print("FIX THIS HACK!!!!!!!!!!!!!!!!!!!!!!!!!")
    tmp = pdata.darrays
    tmp['profile_depth_arrays'] = ['t', 's', 'theta', 'sigma', 'rho']
    #embed(header='137 of binning')
    #print(f'Depths: {bindata["depth"]}')
    bData = pdata.__class__.from_dict(bindata, tmp,
                                      pdata.meta_dict, pdata.dataset,
                                      in_field=pdata.in_field)

    # Add depths
    if pd == 'p':
        bData.p = bindata['p']
    else:
        bData.depth = bindata['depth']
    
    return bData