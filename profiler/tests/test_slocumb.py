""" Tests for Slocum Gliders """

import glob
import numpy as np
import os

apath = os.getenv('ARCTERX')

import pytest

from profiler.gliderdata import SlocumData
from profiler import binning

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_binned_slocum():
    datafile = os.path.join(apath, 'gliders/slocumb/osu685.l3.nc')
    pData = SlocumData.from_binned_file(datafile, 'slocumb', dataset,
                                      missid=60000, in_field=True)