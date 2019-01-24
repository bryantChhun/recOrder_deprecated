#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :1/24/19
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from src.Processing.ReconOrder import ReconOrder
from src.Processing.AzimuthToVector import compute_average

class SignalController(QObject):

    average_computed = pyqtSignal(object)

    def __init__(self, processor):
        super().__init__()
        if isinstance(processor, ReconOrder):
            self._recon = processor
        else:
            raise NotImplementedError("Processor Not Implemented: construct only with ReconOrder")

    @pyqtSlot(object)
    def receive_from_window(self, kernel: object) -> bool:
        if type(kernel) == str:
            print("received update from window: "+str(kernel))
            avg_vectors = self.compute_average(kernel)
            print("transmitting vector to gui: "+str(type(avg_vectors)))
            self.average_computed.emit(avg_vectors)
            return True
        else:
            return False

    def compute_average(self, kernel: str):
        s1 = self._recon.s1
        s2 = self._recon.s2
        retardance = self._recon.retard
        return compute_average(s1,
                               s2,
                               kernel=kernel,
                               retardance=retardance,
                               flipPol=self._recon.flipPol)

    def make_connection(self, gui):
        gui.avg_change.connect(self.receive_from_window)

