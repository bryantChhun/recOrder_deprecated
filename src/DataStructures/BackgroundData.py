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


class BackgroundData(metaclass=Singleton, IntensityData, StokesData, PhysicalData):

    def __init__(self):
        super().__init__()

    def return_none_vals(self):
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
