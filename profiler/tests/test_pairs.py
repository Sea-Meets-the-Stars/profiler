""" Tests for Spray Gliders """

import glob
import numpy as np

import pytest

from profiler import gliderdata
from profiler import floatdata
from profiler import profilepairs
from profiler.specific import em_apex

from IPython import embed

dataset = 'ARCTERX-Leg2'
max_time = 10.
variables = 'dTdTdT'

def test_gliders():

    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/*.mat')
    datafiles.sort()
    arcterx2 = gliderdata.SprayData.from_list(datafiles, dataset, adcp_on=False, in_field=True)
    gPairs = profilepairs.ProfilerPairs([arcterx2], max_time=max_time)

def test_emapex():
    dfile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/EM_Apex/EMApex_data_small_array_19-Feb-2025.mat'
    emapexs = em_apex.load_emapex_infield(dfile, dataset, add_vel=False,
                                        skip_floats=['F10285'])
    nbins = 20
    rbins = 10**np.linspace(0., np.log10(400), nbins) # km
    pPairs = profilepairs.ProfilerPairs(
                emapexs, max_time=10., 
                avoid_same_glider=True, debug=False)

def test_mixed():
    # Mixed
    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/*.mat')
    datafiles.sort()
    arcterx2 = gliderdata.SprayData.from_list(datafiles, dataset, adcp_on=False, in_field=True)
    fData = floatdata.load_dataset(dataset)
    mixPairs = profilepairs.ProfilerPairs([arcterx2, fData], max_time=max_time)

def test_isopycnal():
    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/*.mat')
    datafiles.sort()
    arcterx2 = gliderdata.SprayData.from_list(datafiles, dataset, adcp_on=False, in_field=True)

    # Prep
    gPairs = profilepairs.ProfilerPairs([arcterx2], max_time=max_time)
    gPairs.prep_isopycnals('t')
    gPairs.calc_delta(-25., variables)
    gPairs.calc_Sn(variables)