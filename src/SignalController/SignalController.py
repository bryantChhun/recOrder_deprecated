#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :1/24/19
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6xf

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from src.Processing.ReconOrder import ReconOrder
from src.Processing.AzimuthToVector import compute_average, convert_to_vector

from typing import Union
import numpy as np


class SignalController(QObject):

    vector_computed = pyqtSignal(object)

    def __init__(self, processor):
        super().__init__()

        self.kernel_dict = {'1x1': (1, 1),
                            '3x3': (3, 3),
                            '5x5': (5, 5),
                            '7x7': (7, 7),
                            '9x9': (9, 9),
                            '11x11': (11, 11)}
        self.current_avg_kernel = (1,1)
        self.current_length = 10

        if isinstance(processor, ReconOrder):
            self._recon = processor
        else:
            raise NotImplementedError("Processor Not Implemented: construct only with ReconOrder")

    @pyqtSlot(object)
    def receive_from_window(self, update: Union[str, int, float]):
        if type(update) == str:
            self.current_avg_kernel = self.kernel_dict[update]
            avg_vectors = self.recompute_average(kernel=self.current_avg_kernel, length=self.current_length)
            self.vector_computed.emit(avg_vectors)

        elif type(update) == int or float:
            self.current_length = update
            newlength_vectors = self.recompute_length(length=self.current_length)
            self.vector_computed.emit(newlength_vectors)

    def recompute_average(self, kernel: tuple, length=5):
        s1 = self._recon.s1
        s2 = self._recon.s2
        s3 = self._recon.s3
        azimuth_avg, retard_avg, vector_avg = compute_average(s1,
                                                              s2,
                                                              s3,
                                                              kernel=kernel,
                                                              length=length,
                                                              flipPol=self._recon.flip_pol)
        self._recon.azimuth = azimuth_avg
        self._recon.retard = retard_avg
        return vector_avg

    def recompute_length(self, length: Union[int, float]):
        newlength_vector = convert_to_vector(azimuth=self._recon.azimuth - (0.5 * np.pi),
                                             retardance=self._recon.retard,
                                             stride_x=self.current_avg_kernel[0],
                                             stride_y=self.current_avg_kernel[1],
                                             length=length)
        return newlength_vector

    def make_connection(self, gui):
        gui.average_change.connect(self.receive_from_window)
        gui.length_change.connect(self.receive_from_window)


