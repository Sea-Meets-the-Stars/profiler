""" Tests for Spray Gliders """

import glob

import pytest

from cugn import gliderdata
from cugn import floatdata
from cugn import profilepairs

from IPython import embed

dataset = 'ARCTERX-Leg2'
max_time = 10.
variables = 'dTdTdT'

def test_gliders():

    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/*.mat')
    datafiles.sort()
    arcterx2 = gliderdata.SprayData.from_list(datafiles, dataset, adcp_on=False, in_field=True)
    gPairs = profilepairs.ProfilerPairs([arcterx2], max_time=max_time)

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