""" Tests for Triaxus """

import glob
import numpy as np
import os

apath = os.getenv('ARCTERX')

import pytest

from profiler import triaxusdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_triaxus():
    datafile = os.path.join(apath, 'Triaxus/CTD_03608.000.proc.mat')
    triaxus = triaxusdata.TriaxusData.from_binned_file(datafile, 'triaxus', 
                                       dataset, in_field=True,
                                       missid=50000)