#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/4/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import threading

from src.FileManagement.RetrieveData import RetrieveData
from src.Processing.ReconOrder import ReconOrder


# Todo: allow passing of processing object, arbitrary use of processing object
# Todo:     ideally, we can have processing objects inherit from ABC, such that the same commands are called from here
class LoadFromFiles(QObject):

    recon_complete = pyqtSignal(object)

    '''
    flow controls:
        self.switch answers "Is data rendered to UI? ok to query next image?"
        self.quad answers "have we already rendered this image in this set of four channels?"
    '''
    def __init__(self, processor,  type = "Test", sample_type = "Sample"):
        super().__init__()
        self.type = type
        self.sample_type = sample_type
        self.retrieve_file = RetrieveData()
        if isinstance(processor, ReconOrder):
            self._Recon = processor
        else:
            self._Recon = None

    def set_processor(self, processor):
        self._Recon = processor

    def get_processor(self):
        return self._Recon

    def fetch_and_compute_test_images(self):
        self._Recon.set_frames(5)
        self._Recon.set_state(0, self.retrieve_file.get_array_from_filename('State0', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(1, self.retrieve_file.get_array_from_filename('State1', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(2, self.retrieve_file.get_array_from_filename('State2', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(3, self.retrieve_file.get_array_from_filename('State3', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(4, self.retrieve_file.get_array_from_filename('State4', type=self.type, sample_type=self.sample_type))
        self._Recon.compute_stokes()
        self._Recon.reconstruct_img()
        self.recon_complete.emit(self._Recon)
        return None

    def fetch_and_compute_images(self):
        self.type = "Py4J"
        self._Recon.set_frames(5)
        self._Recon.set_state(0, self.retrieve_file.get_array_from_filename('Cy5', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(1, self.retrieve_file.get_array_from_filename('DAPI', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(2, self.retrieve_file.get_array_from_filename('FITC', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(3, self.retrieve_file.get_array_from_filename('Rhodamine', type=self.type, sample_type=self.sample_type))
        self._Recon.compute_stokes()
        self._Recon.reconstruct_img()
        self.recon_complete.emit(self._Recon)
        return None

    @pyqtSlot(object)
    def report_from_window(self, max_value: object):
        print(str(max_value))

    def make_connection(self, window):
        window.debug.connect(self.report_from_window)

    #Todo: remove or think again about how to multi thread processing.  could call static executor
    def run_test_reconstruction(self):
        t1 = threading.Thread(target=self.fetch_and_compute_test_images())
        t1.start()

    def run_reconstruction(self):
        t1 = threading.Thread(target=self.fetch_and_compute_images())
        t1.start()