#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/4/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import numpy as np
import cv2
import os

from tests.testUtils.testMetrics import testDataPath

from src.FileManagement.FileExceptions import InvalidDataTypeError, InvalidChannelNameError, \
    InvalidDataTypeAndChannelError, GatewayNotEstablishedError

"""
Class to retrieve data and return as np.array
    provides support for only Py4J memory mapped files and Test data for now (12/10/2018)
"""


class RetrieveData:

    def __init__(self):
        self.types = {'Py4J', 'MemMap', 'File', 'Test'}
        self.states = {'State0', 'State1', 'State2', 'State3', 'State4'}
        self.simmap = {'State0':'Iext', 'State1':'I0', 'State2':'I45', 'State3':'I135', 'State4':'I90'}
        self.sample_types = {'Sample1', 'Sample2', 'BG', 'None', 'Simulation1', 'Simulation2', 'Simulation3'}
        self.gate = None

        # this value is should be used only when running tests
        self.testData = testDataPath()

    def set_gateway(self, gateway):
        self.gate = gateway

    def get_gateway(self):
        return self.gate

    def _get_file_name(self, channel_name, type='Py4J', sample_type='None') -> str:
        """
        Returns filename based on the type of data interface and channel name:
        :param channel_name: channel descriptor:
                                one of "Cy5, DAPI, FITC, Rhodamine" for type="Py4J"
                                one of "State0, State1, State2, State3, State4" for type="Test"
        :param type: supports only 'Py4J' or 'Test'
        :param sample_type:
        :return: String filename
        """

        if sample_type not in self.sample_types:
            raise InvalidDataTypeError("Sample Type must be one of: 'Sample1', 'Sample2', 'BG', 'None'")

        if channel_name not in self.states:
            raise InvalidChannelNameError("State must be one of:'State0', 'State1', 'State2', 'State3', 'State4'")

        if type == 'Py4J':
            if not self.gate:
                raise GatewayNotEstablishedError("gateway not set for this Py4J pipeline")
            file = self.gate.retrieveFileByChannelName(channel_name)
            if file:
                return file

            else:
                raise ValueError("no file by channel name exists")
        elif type == 'Test' and sample_type == 'Sample1':
            file = self.testData+"2018_10_02_MouseBrainSlice/SM_2018_1002_1633_1/Pos0/img_000000000_%s - Acquired Image_000.tif" % channel_name
            return file

        elif type == 'Test' and sample_type == 'Sample2':
            file = self.testData+"2018_10_02_MouseBrainSlice/SM_2018_1002_1640_1/Pos0/img_000000000_%s - Acquired Image_000.tif" % channel_name
            return file

        elif type == 'Test' and sample_type == 'Simulation1':
            file = self.testData+"simulated/quarter_wave/%s.npy" % self.simmap[channel_name]
            return file

        elif type == 'Test' and sample_type == 'Simulation2':
            file = self.testData+"simulated/half_wave/%s.npy" % self.simmap[channel_name]
            return file

        elif type == 'Test' and sample_type == 'Simulation3':
            file = self.testData+"simulated/full_wave/%s.npy" % self.simmap[channel_name]
            return file

        elif type == 'Test' and sample_type == 'BG':
            file = self.testData+"2018_10_02_MouseBrainSlice/BG_2018_1002_1625_1/Pos0/img_000000000_%s - Acquired Image_000.tif" % channel_name
            return file

        else:
            raise InvalidDataTypeAndChannelError("Implementation for data type %s and sample type %s not supported"
                                                 % (type, sample_type))

    def get_array_from_filename(self, channel_name, type="Py4J", sample_type='None') -> np.array:
        """
        Returns numpy array based on type of data interface and channel name

        :param channel_name: based on type
        :param type: "Test" or "Py4J"
        :param sample_type: Must be "Sample" or
        :return: numpy array
        """

        if type not in self.types:
            raise InvalidDataTypeError("Type must be one of: 'Py4J', 'MemMap', 'File', 'Test'")

        filename = self._get_file_name(channel_name, type=type, sample_type=sample_type)

        if not os.path.isfile(filename):
            raise FileNotFoundError("no file found with path: "+filename)

        if type =='Py4J':
            return np.memmap(filename, dtype='uint16', offset=0, mode='r', shape=(512, 512, 1))
        elif type == 'Test' and sample_type != 'Simulation1':
            img = cv2.imread(filename, -1)
            return img
        elif type == 'Test' and sample_type == 'Simulation1':
            img = np.load(filename, 'r+')
            return img
            # return img.astype(np.float32, copy=False)
