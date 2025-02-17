""" Tests for Spray Gliders """

import glob

import pytest

from profiler import floatdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_single_float():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/8998.mat'
    s8996 = floatdata.SoloData(datafile, dataset, in_field=True)
