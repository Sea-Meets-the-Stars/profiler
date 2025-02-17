""" Tests for Spray Gliders """

import glob

import pytest

from profiler import gliderdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_single_spray():
    datafile = '/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/0033.mat'
    s33 = gliderdata.SprayData(datafile, dataset, 
                           in_field=True, adcp_on=False)

def test_from_list():

    datafiles = glob.glob('/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/*.mat')
    datafiles.sort()
    arcterx2 = gliderdata.SprayData.from_list(datafiles, dataset, adcp_on=False, in_field=True)