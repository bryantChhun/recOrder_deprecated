#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :2/28/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

import numpy as np
from copy import deepcopy


class IntensityData:
    """
    Data Structure that contains all raw intensity images
    """

    def __init__(self):
        self._IExt = None
        self._I0 = None
        self._I45 = None
        self._I90 = None
        self._I135 = None

    @property
    def IExt(self):
        return self._IExt

    @IExt.setter
    def IExt(self, data: np.ndarray):
        self._IExt = deepcopy(data)

    @property
    def I0(self):
        return self._I0

    @I0.setter
    def I0(self, data: np.ndarray):
        self._I0 = deepcopy(data)

    @property
    def I45(self):
        return self._I45

    @I45.setter
    def I45(self, data: np.ndarray):
        self._I45 = deepcopy(data)

    @property
    def I90(self):
        return self._I90

    @I90.setter
    def I90(self, data: np.ndarray):
        self._I90 = deepcopy(data)

    @property
    def I135(self):
        return self._I135

    @I135.setter
    def I135(self, data: np.ndarray):
        self._I135 = deepcopy(data)


