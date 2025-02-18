""" Tests for VMPs """

import glob
import numpy as np

import pytest

from profiler import triaxusdata

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_triaxus():
    datafile = '/home/xavier/Projects/Oceanography/data/ARCTERX/Triaxus/CTD_03608.000.proc.mat'
    triaxus = triaxusdata.TriaxusData.from_binned_file(datafile, 'triaxus', 
                                       dataset, in_field=True,
                                       missid=50000)
#embed(header='triaxus 19')