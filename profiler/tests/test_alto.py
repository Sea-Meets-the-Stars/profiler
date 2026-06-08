""" Tests for Spray Gliders """

import glob
import numpy as np
import os

apath = os.getenv('ARCTERX')

import pytest

from profiler.specific import altos

from IPython import embed

dataset = 'ARCTERX-Leg2'

def test_binned_alto():
    datafile = os.path.join(apath, 'Floats/Alto/tn441_alto_gridded.mat')
    pDatas = altos.load_infield(datafile, dataset)

#embed(header='18 of test altos')