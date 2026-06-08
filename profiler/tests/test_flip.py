""" Tests for Spray Gliders """

import glob
import numpy as np
import os

apath = os.getenv('ARCTERX')

import pytest

from profiler import floatdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

#def test_binned_flip():
datafile = os.path.join(apath, 'Floats/Flip/4006.mat')
s33 = floatdata.FlipData.from_binned_file(
        datafile, 'idg', dataset, in_field=True)

#s8996 = load_idg.load_raw(datafile, dataset, in_field=True)
