import os
import numpy as np

import pymatreader
from cugn import utils as cugn_utils

from IPython import embed


def load_binned_data(profiler):

    """ Load the CTD data for Arcteryx """
    if os.path.splitext(profiler.datafile)[1][1:] == 'mat':
        d_bin = pymatreader.read_mat(profiler.datafile)
    elif os.path.splitext(profiler.datafile)[1][1:] == 'npz':
        tmp = np.load(profiler.datafile, allow_pickle=True)
        # Hack me
        d_bin = dict(bindata=tmp)
    else: 
        raise IOError(f'Bad reader {profiler.reader}')

    # Scalars
    if not profiler.in_field:
        profiler.scalar_keys += ['x0', 'x1', 'y0', 'y1']
    for key in profiler.scalar_keys:
        setattr(profiler, key, d_bin[profiler.base_key][key])

    # Depth arrays
    for key in profiler.depth_arrays:
        setattr(profiler, key, d_bin[profiler.base_key][key])

    # Profile arrays
    #embed(header='30 of idg_utis')
    if not profiler.in_field:
        profiler.profile_arrays += ['dist', 'offset', 'missid']
    for ss, key in enumerate(profiler.profile_arrays):
        # Set the mask from the first one
        if ss == 0:
            gdi = np.isfinite(d_bin[profiler.base_key][key])
        setattr(profiler, key, d_bin[profiler.base_key][key][gdi])

    # Profile + depth
    if profiler.has_adcp and profiler.adcp_on: 
        profiler.profile_depth_arrays += ['udop', 'vdop', 
                                    'udopacross', 'udopalong']
    for key in profiler.profile_depth_arrays:
        setattr(profiler, key, d_bin[profiler.base_key][key][:,gdi])

    if profiler.in_field:
        # Mission ID
        key = 'missid'
        profiler.profile_arrays += [key]
        #embed(header='53 of loading')
        if profiler.__class__.__name__ == 'EMApexData':
            base = os.path.basename(profiler.datafile).split('.')[0]
            missid = int(base.split('F')[1])
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
        dist, offset = cugn_utils.calc_dist_offset('None',
            profiler.lon, profiler.lat, endpoints=(lonendpts, latendpts))
        # Fill in
        profiler.dist = dist
        key = 'offset'
        profiler.profile_arrays += [key]
        profiler.offset = offset