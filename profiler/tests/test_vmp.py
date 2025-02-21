""" Tests for VMPs """

import glob
import numpy as np

import os

apath = os.getenv('ARCTERX')

import pytest

from profiler import vmpdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_vmp():
    datafile = os.path.join(apath, 'ARCTERX/VMP/combo.nc')
    vmp = vmpdata.VMPData.from_binned_file(datafile, 'cusack', 
                                       dataset, in_field=True,
                                       missid=20000)
#embed(header='test_vmp 19')

#s8996 = load_idg.load_raw(datafile, dataset, in_field=True)

#def test_raw_solo():
#    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Floats/Solo/Raw/8999.mat'
#    s8996 = floatdata.SoloData(datafile, dataset, in_field=True)