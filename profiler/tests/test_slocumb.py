""" Tests for Spray Gliders """

import glob
import numpy as np

import pytest

from profiler.specific import em_apex
from profiler import binning

from IPython import embed

dataset = 'ARCTERX-Leg2'

#def test_raw_apex():
    # Apex
datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/gliders/slocumb/osu685.l3.nc'
pDatas = em_apex.load_emapex_infield(dfile, dataset)

embed(header='26 of test apex')

#def test_bin_raw_apex():
    # Apex
dfile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/EM_Apex/EMApex_data_small_array_17-Feb-2025.mat'
pDatas = em_apex.load_emapex_infield(dfile, dataset)
    # Bin
bData = binning.bin_profilerdata(pDatas[0], add_vel=False)

embed(header='26 of test apex')