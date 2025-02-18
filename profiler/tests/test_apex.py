""" Tests for Spray Gliders """

import glob
import numpy as np

import pytest

from profiler import floatdata
from profiler.utils import apex_utils
from profiler import binning
from profiler.loading import em_apex 

from IPython import embed

dataset = 'ARCTERX-Leg2'

#def test_raw_apex():
    # Apex
dfile = '/run/user/1000/gvfs/smb-share:server=10.43.20.20,share=cruiseshare/Data/floats/EM_Apex/EMApex_data_small_array_17-Feb-2025.mat'
pDatas = em_apex.load_emapex_infield(dfile, dataset)
embed(header='21 of test')

# Binning
#key = list(d.keys())[0]
#bindata = binning.run(d[key], add_vel=False)

def test_binned_apex():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/EM_Apex/EM_Apex_F10281.npz'
    f10281 = floatdata.EMApexData(datafile, dataset, in_field=True)
