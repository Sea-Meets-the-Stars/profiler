""" Tests for Spray Gliders """

import glob
import numpy as np
import os

apath = os.getenv('ARCTERX')

import pytest

from profiler import floatdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_raw_solo():
    datafile = os.path.join(apath, 'Floats/Solo/Raw/8999.mat')
    s8996 = floatdata.SoloData.from_rawfile(
        datafile, dataset, in_field=True)

def test_binned_solo():
    datafile = os.path.join(apath, 'Floats/Solo/Raw/8999.mat')
    s33 = floatdata.SoloData.from_binned_file(
        datafile, 'idg', dataset, in_field=True)

#s8996 = load_idg.load_raw(datafile, dataset, in_field=True)
