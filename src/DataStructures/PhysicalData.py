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


class PhysicalData(object):
    """
    Data Structure that contains all computed physical data
    """

    _I_trans = None
    _retard = None
    _retard_nm = None
    _polarization = None
    _scattering = None
    _azimuth = None
    _azimuth_vector = None
    _azimuth_degree = None

    def __init__(self):
        super(PhysicalData, self).__init__()

    def __setattr__(self, name, value):
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set name %r on object of type %s' % (
                name, self.__class__.__name__))

    @property
    def I_trans(self):
        return self._I_trans

    @I_trans.setter
    def I_trans(self, data: np.ndarray):
        self._I_trans = deepcopy(data)

    @property
    def retard(self):
        return self._retard

    @retard.setter
    def retard(self, data: np.ndarray):
        self._retard = deepcopy(data)

    @property
    def retard_nm(self):
        return self._retard_nm

    @retard_nm.setter
    def retard_nm(self, data : np.ndarray):
        self._retard_nm = data

    @property
    def polarization(self):
        return self._polarization

    @polarization.setter
    def polarization(self, data: np.ndarray):
        self._polarization = deepcopy(data)

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, data: np.ndarray):
        self._azimuth = deepcopy(data)

    @property
    def azimuth_vector(self):
        return self._azimuth_vector

    @azimuth_vector.setter
    def azimuth_vector(self, data: np.ndarray):
        self._azimuth_vector = deepcopy(data)

    @property
    def azimuth_degree(self):
        return self._azimuth_degree

    @azimuth_degree.setter
    def azimuth_degree(self, data: np.ndarray):
        self._azimuth_degree = deepcopy(data)

    @property
    def scattering(self):
        return self._scattering

    @scattering.setter
    def scattering(self, data: np.ndarray):
        self._scattering = deepcopy(data)


