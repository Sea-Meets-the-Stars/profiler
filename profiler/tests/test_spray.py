""" Tests for Spray Gliders """

import glob
import os

apath = os.getenv('ARCTERX')

import pytest

from profiler import gliderdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_binned_spray():
    datafile = os.path.join(apath, 'gliders/spray/0033.mat')
    s33 = gliderdata.SprayData.from_binned_file(
        datafile, 'idg', dataset, in_field=True,
        extra_dict={'adcp_on': False})