import os
import numpy as np

from profiler.loading.pymatreader import pymatreader
import xarray
import pandas

from profiler.utils import offsets

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from profiler.profilerdata import ProfilerData

from IPython import embed

def set_profiler(profiler:"ProfilerData", 
                 key:str, data, bin_style:str, gdi:np.ndarray=None):
    """ Set a profiler attribute from a binned dataset

    Args:
        profiler (ProfilerData): The profiler object
        key (str): The key to set
        data (_type_): The data object
        bin_style (str): The binning style
        gdi (np.ndarray, optional): The good data indices

    Raises:
        IOError: If the data type is not recognized
    """

    if isinstance(data[key], xarray.core.dataarray.DataArray):
        idata = data[key].values
    elif isinstance(data[key], np.ndarray):
        if bin_style in ['idg', 'triaxus']:
            idata = data[key].T
        else:
            idata = data[key]
    elif isinstance(data[key], (float, int, str)): # Scalars
        idata = data[key]
    else:
        embed(header='16 of binned')
        raise IOError("update!!")

    # gdi?
    if gdi is not None:
        idata = idata[gdi]

    setattr(profiler, key, idata)


def load(profiler, bin_style:str, in_missid:int=None):
    """ Load a binned dataset 

    The binned dataset is loaded into the profiler object

    Args:
        profiler (ProfilerData): The profiler object
        bin_style (str): The binning style
        in_missid (int, optional): The mission ID

    Raises:
        IOError: If the binning style is not recognized

    """
    if bin_style == 'idg':  # Scripps
        d = pymatreader.read_mat(profiler.datafile)
        if 'bindata' in d:
            d_bin = d['bindata']
        elif 'ctd' in d:
            d_bin = d['ctd']
        else:
            raise IOError(f'Bad binning style {bin_style} for {profiler.datafile}')
        # Deal with OSU velocity -- this is in development
        #if profiler.adcp_on and 'v' in d_bin:
        #    # OSU velocity
        #    d_bin['udop'] = d_bin['u']
        #    d_bin['vdop'] = d_bin['v']
        #    embed(header='79 of binned')
    elif bin_style == 'cusack': # OSU Jesse Cusack (VMP)
        d_bin = xarray.load_dataset(profiler.datafile)
        d_bin['depth'] = d_bin.bin.values
        # Time
        ptimes = [pandas.Series(item).mean().timestamp() for item in pandas.to_datetime(d_bin.time.values)]
        d_bin = d_bin.drop_vars('time')
        d_bin['time'] = (['profile'], ptimes)
        d_bin['t'] = d_bin['temp']
        d_bin['s'] = d_bin['SP']
    elif bin_style == 'triaxus': # Triaxus
        d = pymatreader.read_mat(profiler.datafile, 
                                 verify_compressed_data_integrity=True)  # FAILED
        d_bin = d['pr']
        d_bin['time'] = (1735689600 +  # This is Unix time for 2025-01-01 00:00:00 UTC
            (d_bin['t'] * 86400)) # seconds
        # Rename me + transpose
        d_bin['t'] = d_bin['T'].astype(np.float64) # Deals with bogus complex numbers
        d_bin['s'] = d_bin['S'].astype(np.float64) # Deals with bogus complex numbers
        d_bin['sigma'] = d_bin['sigma_t'].astype(np.float64) # Deals with bogus complex numbers
    elif bin_style == 'slocum': # OSU Jesse Cusack 
        d_bin = xarray.load_dataset(profiler.datafile)
        d_bin['depth'] = d_bin.depth.values
        # Time
        ptimes = [pandas.Series(item).mean().timestamp() for item in pandas.to_datetime(d_bin.profile_time.values)]
        d_bin['time'] = (['profile_id'], ptimes)
        #embed(header='72 of binned')
        d_bin['t'] = (['profile_id','z'], d_bin['temperature'].values.T)
        d_bin['s'] = (['profile_id','z'], d_bin['salinity'].values.T)
        d_bin['SA'] = (['profile_id','z'], d_bin['SA'].values.T)
        # Average lat, lon to get a single value
        d_bin['lat'] = d_bin['lat'].mean(dim='z')
        d_bin['lon'] = d_bin['lon'].mean(dim='z')
    elif bin_style == 'seaglider': # Up/down measurements by Luc Rainville
        d = xarray.load_dataset(profiler.datafile)
        # Reduce dataset to finite time_dive values
        if np.any(np.isnan(d.time_dive)):
            print("Warning: NaN values in time_dive, dropping those profiles")
            # If there are NaN values, drop them
            d = d.where(np.isfinite(d.time_dive), drop=True)
        # Dummy ds
        new_coords = dict(profile_id=d.profile.values,
                          z=d.z_data_point.values)
        d_bin = xarray.Dataset(coords=new_coords)
        # Grab em
        dives = np.unique(d.dive.values)
        dsav = {}

        # Average the dives
        for ss, dive in enumerate(dives):
            dtmp = d.where(d.dive == dive, drop=True)
            tmp = dtmp.mean('half_profile_data_point')

            for new_key, old_key in zip(['t', 's'], 
                                    ['T', 'S']):
                if ss == 0:
                    dsav[new_key] = []
                # Get the dives
                dsav[new_key].append(tmp[old_key].values)

        # Time, lat, lon
        for key in ['time', 'lat', 'lon']:
            d_bin[key] = (['profile_id'], d[f'{key}_dive'].values)
        #embed(header='seaglider 129')
        for key in ['t', 's']:
            d_bin[key] = (['profile_id','z'], dsav[key])
        d_bin['depth'] = d_bin.z.values
        # Time
        ptimes = [pandas.Series(item).mean().timestamp() 
                      for item in pandas.to_datetime(d_bin.time.values)]
        d_bin = d_bin.drop_vars('time')
        d_bin['time'] = (['profile_id'], ptimes)
    else: 
        raise IOError(f'Bad reader {profiler.reader}')

    if 'platform' in d_bin:
        profiler.platform = d_bin['platform']

    # Scalars
    if not profiler.in_field:
        profiler.scalar_keys += ['x0', 'x1', 'y0', 'y1']
    for key in profiler.scalar_keys:
        if key in d_bin:
            # If the key is in the binned data, set it
            set_profiler(profiler, key, d_bin, bin_style)
        else:
            print(f"Warning: {key} not in binned data for {profiler.datafile}")

    # Depth arrays
    for key in profiler.depth_arrays:
        set_profiler(profiler, key, d_bin, bin_style)

    # Profile arrays
    if not profiler.in_field:
        pass
        # THESE ARE NOT WORKING YET
        #profiler.profile_arrays += ['dist', 'offset']
    for ss, key in enumerate(profiler.profile_arrays):
        # Set the mask from the first one
        if ss == 0:
            #if isinstance(d_bin[key], xarray.core.dataarray.DataArray):
            #    gdi = np.isfinite(d_bin[key].values)
            #else:
            gdi = np.isfinite(d_bin[key])
            # In mission id?
            if in_missid is not None:
                if 'missid' in d_bin:
                    gdi &= (d_bin['missid'] == in_missid)
            # IDs
            profiler.profile_id = np.arange(len(d_bin[key]))[gdi]
        try:
            set_profiler(profiler, key, d_bin, bin_style, gdi=gdi)#[key][gdi])
        except:
            embed(header='100 of binned')


    # Profile + depth
    if profiler.has_adcp and profiler.adcp_on:
        profiler.profile_depth_arrays += ['udop', 'vdop']#, 'udopacross', 'udopalong']
    for key in profiler.profile_depth_arrays:
        try:
            set_profiler(profiler, key, d_bin, bin_style, gdi=gdi)
        except:
            print("Warning: Could not set key", key)
            #embed(header='192 of binned')

    # This breaks for Spray + ARCTERX Leg2
    if profiler.in_field:
        # Mission ID
        key = 'missid'
        #profiler.profile_arrays += [key]
        #embed(header='53 of loading')
        if in_missid is not None:
            missid = in_missid
        elif profiler.__class__.__name__ == 'EMApexData':
            base = os.path.basename(profiler.datafile).split('.')[0]
            missid = int(base.split('F')[1])
        elif profiler.__class__.__name__ == 'SeagliderData':
            base = os.path.basename(profiler.datafile).split('.')[0]
            missid = int(base.split('_')[0][2:])
        #elif profiler.__class__.__name__ in ['VMPData', 'TriaxusData']:
        #    missid = in_missid
        elif profiler.__class__.__name__ == 'SprayData':
            missid = int(os.path.basename(profiler.datafile).split('_')[0])
        else:
            missid = int(os.path.basename(profiler.datafile).split('.')[0])
        setattr(profiler, key, missid)
        profiler.meta_keys.append(key)

    # Generate dist and offset
    #  distE is distance to the North from the median lon (km)
    #  distN is distance to the East from the median lon
    profiler.med_lon = np.median(profiler.lon)
    profiler.med_lat = np.median(profiler.lat)
    latendpts = (profiler.med_lat-0.001, profiler.med_lat+0.001)
    lonendpts = (profiler.med_lon, profiler.med_lon)

    # distE
    key = 'distE'
    profiler.profile_arrays += [key]
    distN, distW = offsets.calc_dist_offset(
        profiler.lon, profiler.lat, (lonendpts, latendpts))
    profiler.distE = -1*distW
    profiler.data_keys.append(key)

    # distN
    key = 'distN'
    profiler.profile_arrays += [key]
    profiler.distN = distN
    profiler.data_keys.append(key)

    # Mission ID
    if in_missid is not None:
        key = 'missid'
        setattr(profiler, key, in_missid)
        profiler.meta_keys.append(key)