""" Tests for Spray Gliders """

import pytest
import glob
import os

from profiler import gliderdata
from profiler import profilers_io

from IPython import embed

dataset = 'ARCTERX-Leg2'
apath = os.path.join(os.getenv('OS_ARCTERX'), '2025_IOP')

def test_write_tojson():
    # Load
    datafile = os.path.join(apath, 'gliders/spray/0033.mat')
    s33 = gliderdata.SprayData.from_binned_file(
            datafile, 'idg', dataset, in_field=True,
            extra_dict={'adcp_on': False})

    # Write
    s33.write('tst.json')

def test_write_profilers():
    # Load
    datafiles = glob.glob(os.path.join(apath, 'gliders/spray/*.mat'))
    sprays = []
    for datafile in datafiles:
        s = gliderdata.SprayData.from_binned_file(
            datafile, 'idg', dataset, in_field=True,
            extra_dict={'adcp_on': False})
        sprays.append(s)
    # Write
    profilers_io.write_profilers(sprays, 'tst_profilers.json')