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
        if profiler.in_field:
            base_key = 'bindata'
        else:
            base_key = 'ctd'
        d_bin = pymatreader.read_mat(profiler.datafile)[base_key]
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
        #embed(header='47 of binned')
        d_bin['time'] = (1735689600 +  # This is Unix time for 2025-01-01 00:00:00 UTC
            (d_bin['t'] * 86400)) # seconds
        # Rename me + transpose
        d_bin['t'] = d_bin['T']
        d_bin['s'] = d_bin['S']
        d_bin['sigma'] = d_bin['sigma_t']
    elif bin_style == 'slocumb': # OSU Jesse Cusack (VMP)
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
    else: 
        raise IOError(f'Bad reader {profiler.reader}')

    if 'platform' in d_bin:
        profiler.platform = d_bin['platform']

    # Scalars
    if not profiler.in_field:
        profiler.scalar_keys += ['x0', 'x1', 'y0', 'y1']
    for key in profiler.scalar_keys:
        set_profiler(profiler, key, d_bin, bin_style)

    # Depth arrays
    for key in profiler.depth_arrays:
        set_profiler(profiler, key, d_bin, bin_style)

    # Profile arrays
    if not profiler.in_field:
        profiler.profile_arrays += ['dist', 'offset']
    for ss, key in enumerate(profiler.profile_arrays):
        # Set the mask from the first one
        if ss == 0:
            #if isinstance(d_bin[key], xarray.core.dataarray.DataArray):
            #    gdi = np.isfinite(d_bin[key].values)
            #else:
            gdi = np.isfinite(d_bin[key])
        try:
            set_profiler(profiler, key, d_bin, bin_style, gdi=gdi)#[key][gdi])
        except:
            embed(header='100 of binned')

    #embed(header='84 of binned')

    # Profile + depth
    if profiler.has_adcp and profiler.adcp_on:
        profiler.profile_depth_arrays += ['udop', 'vdop', 
                                    'udopacross', 'udopalong']
    for key in profiler.profile_depth_arrays:
        try:
            set_profiler(profiler, key, d_bin, bin_style, gdi=gdi)
        except:
            embed(header='112 of binned')

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
        #elif profiler.__class__.__name__ in ['VMPData', 'TriaxusData']:
        #    missid = in_missid
        else:
            missid = int(os.path.basename(profiler.datafile).split('.')[0])
        setattr(profiler, key, missid)

        # Generate dist and offset
        #  dist is distance to the North from the median lon (km)
        #  offset is distance to the East from the median lon
        profiler.med_lon = np.median(profiler.lon)
        profiler.med_lat = np.median(profiler.lat)
        latendpts = (profiler.med_lat-1., profiler.med_lat+1.)
        lonendpts = (profiler.med_lon, profiler.med_lon)

        # dist
        key = 'dist'
        profiler.profile_arrays += [key]
        dist, offset = offsets.calc_dist_offset(
            profiler.lon, profiler.lat, (lonendpts, latendpts))
        # Fill in
        profiler.dist = dist
        key = 'offset'
        profiler.profile_arrays += [key]
        profiler.offset = offset
