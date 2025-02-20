""" Tests for Spray Gliders """

import glob
import numpy as np

import pytest

from profiler.gliderdata import SlocumbData
from profiler import binning

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_binned_slocumb():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/gliders/slocumb/osu685.l3.nc'
    pData = SlocumbData.from_binned_file(datafile, 'slocumb', dataset,
                                      missid=60000, in_field=True)