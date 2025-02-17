""" Tests for Spray Gliders """

import glob
import numpy as np

import pytest

from profiler import floatdata
from profiler.utils import apex_utils
from profiler import binning

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_solo():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Solo/8998.mat'
    s8996 = floatdata.SoloData(datafile, dataset, in_field=True)

def test_raw_apex():
    # Apex
    dfile = '/run/user/1000/gvfs/smb-share:server=10.43.20.20,share=cruiseshare/Data/floats/EM_Apex/EMApex_data_small_array_17-Feb-2025.mat'
    d = apex_utils.process_apex_floats(dfile)

    # Binning
    key = list(d.keys())[0]
    bindata = binning.run(d[key], add_vel=False)

def test_binned_apex():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/EM_Apex/EM_Apex_F10281.npz'
    f10281 = floatdata.EMApexData(datafile, dataset, in_field=True)
