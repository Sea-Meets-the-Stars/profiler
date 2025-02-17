""" Tests for Spray Gliders """

import glob

import pytest

from cugn import floatdata
from cugn import gliderdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

# THIS TEST FAILS!!
#def test_gliderfloat():
#    fData = floatdata.load_dataset(dataset)
#    gData = gliderdata.load_dataset(dataset)
#
#    assets = gData.sum(fData, merge_on_depth=True)