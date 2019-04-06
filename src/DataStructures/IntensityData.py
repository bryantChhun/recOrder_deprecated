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
    _IExt = None
    _I0 = None
    _I45 = None
    _I90 = None
    _I135 = None

    def __init__(self):
        super(IntensityData, self).__init__()

    def __setattr__(self, name, value):
        """
        do not allow assignment of attributes other than those defined above
        :param name: attribute
        :param value: value
        :return:
        """
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set name %r on object of type %s' % (
                name, self.__class__.__name__))

    def set_angle_from_index(self, index: int, image: np.ndarray):
        """
        The order is based on the initial conditions in the paper.
            Paper init cond: assume a horizontally polarized init state
            Physical condition: assume a vertically polarized init state
            So all the I(deg) values are actually rotated 90 degrees
        :param index: state index
        :param image: data
        :return:
        """
        if index == 0:
            self.IExt = image
        elif index == 1:
            self.I90 = image
        elif index == 2:
            self.I135 = image
        elif index == 3:
            self.I45 = image
        elif index == 4:
            self.I0 = image

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


