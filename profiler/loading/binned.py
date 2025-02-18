import os
import numpy as np

import pymatreader
import xarray

from profiler.utils import offsets 

from IPython import embed

def set_profiler(profiler, key, data, gdi:np.ndarray=None):

    if isinstance(data[key], xarray.core.dataarray.DataArray):
        idata = data[key].values
    else:
        embed(header='16 of binned')
        raise IOError("update!!")

    # gdi?
    if gdi is not None:
        idata = idata[gdi]

    setattr(profiler, key, idata)


def load(profiler, bin_style:str, in_missid:int=None):
    """ Load a binned dataset """
    
    if bin_style == 'idg':  # Scripps
        if profiler.in_field:
            base_key = 'bindata'
        else:
            base_key = 'ctd'
        embed(header='NEED TO TRANSPOSE!!')
        d_bin = pymatreader.read_mat(profiler.datafile)[base_key]
    elif bin_style == 'cusack': # OSU Jesse Cusack (VMP)
        d_bin = xarray.load_dataset(profiler.datafile)
        d_bin['depth'] = d_bin.bin.values
        # Rename a few (maybe move this to a dict)
        d_bin['depth'] = d_bin.bin.values
        d_bin['t'] = d_bin['temp']
        d_bin['s'] = d_bin['SP']
        d_bin['SA'] = d_bin['SA']
    else: 
        raise IOError(f'Bad reader {profiler.reader}')

    if 'platform' in d_bin:
        profiler.platform = d_bin['platform']

    # Scalars
    if not profiler.in_field:
        profiler.scalar_keys += ['x0', 'x1', 'y0', 'y1']
    for key in profiler.scalar_keys:
        set_profiler(profiler, key, d_bin)

    # Depth arrays
    for key in profiler.depth_arrays:
        set_profiler(profiler, key, d_bin)

    # Profile arrays
    #embed(header='30 of idg_utis')
    if not profiler.in_field:
        profiler.profile_arrays += ['dist', 'offset', 'missid']
    for ss, key in enumerate(profiler.profile_arrays):
        # Set the mask from the first one
        if ss == 0:
            gdi = np.isfinite(d_bin[key])
        set_profiler(profiler, key, d_bin, gdi=gdi)#[key][gdi])

    # Profile + depth
    if profiler.has_adcp and profiler.adcp_on: 
        profiler.profile_depth_arrays += ['udop', 'vdop', 
                                    'udopacross', 'udopalong']
    for key in profiler.profile_depth_arrays:
        set_profiler(profiler, key, d_bin, gdi=gdi)

    if profiler.in_field:
        # Mission ID
        key = 'missid'
        profiler.profile_arrays += [key]
        #embed(header='53 of loading')
        if profiler.__class__.__name__ == 'EMApexData':
            base = os.path.basename(profiler.datafile).split('.')[0]
            missid = int(base.split('F')[1])
        elif profiler.__class__.__name__ == 'VMPData':
            missid = in_missid
        else:
            missid = int(os.path.basename(profiler.datafile).split('.')[0])
        setattr(profiler, key, missid*np.ones_like(profiler.lat, dtype=int))

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


def load_raw(datafile:str):

    # Load
    f = pymatreader.read_mat(datafile)
    data = f['data']

    #
    darrays = {}
    iprof = {}
    # Count em
    nDepths = [len(item) for item in data['t']]
    Nprof = len(data['t'])
    Ndepth = np.max(nDepths)
    
    # Profile arrays
    darrays['profile_arrays'] = ['time', 'lat', 'lon']
    for key in darrays['profile_arrays']:
        iprof[key] = data[key][:,1]

    # Depth arrays
    darrays['depth_arrays'] = []

    darrays['profile_depth_arrays'] = ['t', 's', 'depth', 
                                       'theta', 'sigma', 'rho', 'p']
    # Profile + Depth arrays
    for key in darrays['profile_depth_arrays']:
        if key not in iprof:
            iprof[key] = np.ones((Nprof, Ndepth))*np.nan
        for pp in range(Nprof):
            iprof[key][pp, :nDepths[pp]] = data[key][pp]

    # Qual vals
    iprof['qual'] = {}
    for key in ['t', 's', 'depth', 'theta', 'sigma', 'rho', 'p']:
        if key == 't':
            iprof['qual'][key] = data['qual'][key]
        else:
            iprof['qual'][key] = data['qual']['s']

    # Return
    return iprof, darrays
            