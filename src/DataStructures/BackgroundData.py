#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :2/28/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

from src.DataStructures.IntensityData import IntensityData
from src.DataStructures.StokesData import StokesData
from src.DataStructures.PhysicalData import PhysicalData


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BackgroundData(IntensityData, StokesData, PhysicalData, metaclass=Singleton):

    def __setattr__(self, name, value):
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set name %r on object of type %s' % (
                name, self.__class__.__name__))

    def __init__(self):
        super(BackgroundData, self).__init__()

    def assign_intensity(self, int_obj: IntensityData):
        self.IExt = int_obj.IExt
        self.I0 = int_obj.I0
        self.I45 = int_obj.I45
        self.I90 = int_obj.I90
        self.I135 = int_obj.I135

    def assign_stokes(self, stk_obj: StokesData):
        self.s0 = stk_obj.s0
        self.s1 = stk_obj.s1
        self.s2 = stk_obj.s2
        self.s3 = stk_obj.s3

    def assign_physical(self, phy_obj: PhysicalData):
        self.I_trans = phy_obj.I_trans
        self.retard = phy_obj.retard
        self.polarization = phy_obj.polarization
        self.azimuth = phy_obj.azimuth
        self.azimuth_degree = phy_obj.azimuth_degree
        self.azimuth_vector = phy_obj.azimuth_vector
        self.scattering = phy_obj.scattering

    def print_none_vals(self):
        """
        prints to console all attributes that are NOT assigned

        :return:
        """
        intensity = ['IExt', 'I0', 'I45', 'I90', 'I135']
        stokes = ['s0', 's1', 's2', 's3', 's4']
        physical = ['I_trans', 'retard', 'polarization', 'azimuth', 'scattering']
        for image in intensity:
            if getattr(self, image) is None:
                print("value not set = "+str(image))
        for image in stokes:
            if getattr(self, image) is None:
                print("value not set = "+str(image))
        for image in physical:
            if getattr(self, image) is None:
                print("value not set = "+str(image))
