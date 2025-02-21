""" Tests for Spray Gliders """

import glob
import numpy as np

import os

apath = os.getenv('ARCTERX')

import pytest

from profiler.specific import em_apex
from profiler import binning

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_raw_apex():
    # Apex
    dfile = os.path.join(apath, 'EM_Apex/EMApex_data_small_array_17-Feb-2025.mat')
    pDatas = em_apex.load_emapex_infield(dfile, dataset)

def test_bin_raw_apex():
    # Apex
    dfile = os.path.join(apath, 'EM_Apex/EMApex_data_small_array_17-Feb-2025.mat')
    pDatas = em_apex.load_emapex_infield(dfile, dataset)
    # Bin
    bData = binning.bin_profilerdata(pDatas[0], add_vel=False)

#embed(header='26 of test apex')