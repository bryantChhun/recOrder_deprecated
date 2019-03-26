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


class StokesData(object):
    """
    Data Structure that contains all stokes vector images
    """

    def __init__(self):
        super(StokesData, self).__init__()
        self._s0 = None
        self._s1 = None
        self._s2 = None
        self._s3 = None
        self._A = None
        self._B = None

    # private properties?
    @property
    def A(self):
        return self._A

    @A.setter
    def A(self, value):
        if value is True:
            self._A = self.s1 / self.s3
        else:
            self._A = value
            # print("normalized s1 (A) cannot be set. Assign s1 or s3 to calculate")


    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, value):
        if value is True:
            self._B = -self.s2 / self.s3
        else:
            self._B = value
            # print("normalized s2 (B) cannot be set. Assign s2 or s3 to calculate")


    # public properties
    @property
    def s0(self):
        return self._s0

    @s0.setter
    def s0(self, data: np.ndarray):
        self._s0 = deepcopy(data)

    @property
    def s1(self):
        return self._s1

    @s1.setter
    def s1(self, data: np.ndarray):
        """
        s1 vector
        automatically calculates normalized value if s3 is set
        :param data: np.ndarray
        :return:
        """
        self._s1 = deepcopy(data)
        if self._s3 is not None:
            self.A = True

    @property
    def s2(self):
        return self._s2

    @s2.setter
    def s2(self, data: np.ndarray):
        """
        s2 vector
        automatically calculates normalized value if s3 is set
        :param data: np.ndarray
        :return:
        """
        self._s2 = deepcopy(data)
        if self._s3 is not None:
            self.B = True

    @property
    def s3(self):
        return self._s3

    @s3.setter
    def s3(self, data: np.ndarray):
        """
        s3 vector
        automatically calculates normalized s1 and s2 if each are set
        :param data:
        :return:
        """
        self._s3 = deepcopy(data)
        if self._s1 is not None:
            self.A = True
        if self._s2 is not None:
            self.B = True
