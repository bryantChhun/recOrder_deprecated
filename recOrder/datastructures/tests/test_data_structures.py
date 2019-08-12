#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :3/29/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

from ..IntensityData import IntensityData
import numpy as np


def test_int_dat_0():
    int_obj = IntensityData()
    int_obj.IExt = np.ones(shape=(5,5))

def test_int_dat_1():
    int_obj = IntensityData()
    int_obj.I0 = np.ones(shape=(5,5))