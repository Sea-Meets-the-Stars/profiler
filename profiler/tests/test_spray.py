""" Tests for Spray Gliders """

import glob

import pytest

from profiler import gliderdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_binned_spray():
    datafile = '/home/xavier/Projects/Oceanography/data/Spray/ARCTERX/Leg2/0033.mat'
    s33 = gliderdata.SprayData.from_binned_file(
        datafile, 'idg', dataset, in_field=True,
        extra_dict={'adcp_on': False})