""" Tests for Spray Gliders """

import glob
import numpy as np

import pytest

from profiler import floatdata
from profiler.loading import idg as load_idg
from profiler import binning

from IPython import embed

dataset = 'ARCTERX-Leg2'

#def test_raw_solo():
datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Solo/Raw/8999.mat'
s8996 = floatdata.SoloData.from_rawfile(datafile, dataset, in_field=True)
embed(header='test_raw_solo 19')

#s8996 = load_idg.load_raw(datafile, dataset, in_field=True)

#def test_raw_solo():
#    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Solo/Raw/8999.mat'
#    s8996 = floatdata.SoloData(datafile, dataset, in_field=True)