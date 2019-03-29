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


class IntensityData(object):
    """
    Data Structure that contains all raw intensity images
    """

    def __setattr__(self, name, value):
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set name %r on object of type %s' % (
                name, self.__class__.__name__))

    def __init__(self):
        super(IntensityData, self).__init__()
        self._IExt = None
        self._I0 = None
        self._I45 = None
        self._I90 = None
        self._I135 = None

    def set_angle_from_index(self, index: int, image: np.ndarray):
        if index == 0:
            self.IExt = image
        elif index == 1:
            self.I0 = image
        elif index == 2:
            self.I45 = image
        elif index == 3:
            self.I90 = image
        elif index == 4:
            self.I135 = image

    def print_none_vals(self):
        intensity = ['IExt', 'I0', 'I45', 'I90', 'I135']
        for image in intensity:
            if getattr(self, image) is None:
                print("value not set = "+str(image))

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


