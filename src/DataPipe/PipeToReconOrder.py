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

from datetime import datetime


def timer(func):
    def timer_wrap(*args, **kwargs):
        start = datetime.now()
        func(*args,**kwargs)
        stop = datetime.now()
        print( (stop-start).microseconds)
    return timer_wrap


# Todo: allow passing of processing object, arbitrary use of processing object
# Todo:     ideally, we can have processing objects inherit from ABC, such that the same commands are called from here
class PipeToReconOrder(QObject):

    recon_complete = pyqtSignal(object)

    def __init__(self,  type = "Test", sample_type = "Sample1"):
        super().__init__()
        self.type = type
        self.sample_type = sample_type
        self.retrieve_file = RetrieveData()
        self._Recon = None

    def set_processor(self, processor):
        if isinstance(processor, ReconOrder):
            self._Recon = processor
            return True
        else:
            self._Recon = None
            raise ValueError("processor wrong type")

    def get_processor(self):
        return self._Recon

    @timer
    def fetch_images(self):
        print('fetching images')
        self._Recon.set_state(0, self.retrieve_file.get_array_from_filename('State0', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(1, self.retrieve_file.get_array_from_filename('State1', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(2, self.retrieve_file.get_array_from_filename('State2', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(3, self.retrieve_file.get_array_from_filename('State3', type=self.type, sample_type=self.sample_type))
        if self._Recon.frames == 5:
            self._Recon.set_state(4, self.retrieve_file.get_array_from_filename('State3', type=self.type,
                                                                                sample_type=self.sample_type))
        return True

    #todo: could probably move these to a more appropriate class
    @timer
    def compute_stokes(self):
        print("compute stokes")
        self._Recon.compute_stokes()
        return True

    @timer
    def compute_jones(self):
        print("compute jones")
        self._Recon.compute_jones()
        return True

    @timer
    def compute_inst_matrix(self):
        print("compute inst matrix")
        self._Recon.compute_inst_matrix()
        return True

    @timer
    def correct_background(self, background : object):
        print("correct background")
        self._Recon.correct_background(background)
        return True

    @timer
    def correct_background_localGauss(self):
        print("correct background local gauss")
        self._Recon.correct_background_localGauss()
        return True

    @timer
    def reconstruct_image(self):
        print("Reconstruct image")
        self._Recon.reconstruct_img()
        self.recon_complete.emit(self._Recon)
        return True

    def fetch_and_compute_stokes(self):
        self.fetch_images()
        self.compute_stokes()

    def fetch_and_compute_jones(self):
        self.fetch_images()
        self.compute_jones()

    def fetch_and_correct_background_and_recon_image(self, background: object):
        '''
        Performs both standard background correction from BG images AND
            local background correction using GaussianBlur
        :param background: ReconOrder object that contains stokes calculations for BG images
        :return: True if successful
        '''
        self.fetch_images()
        self.compute_stokes()
        # self.compute_jones()
        self.correct_background(background)
        #self.correct_background_localGauss()
        self.reconstruct_image()

    # to receive callbacks from GUI
    @pyqtSlot(object)
    def report_from_window(self, max_value: object):
        print(str(max_value))

    def make_connection(self, window):
        window.debug.connect(self.report_from_window)

    '''
    Threads for running reconstruction.  Needed to prevent blocking UI.
        Pyqt slots/signals will notify UI that data is ready.
    '''

    #Todo: remove or think again about how to multi thread processing.  could call static executor
    def run_reconstruction(self, threaded = False):
        if threaded:
            t1 = threading.Thread(target=self.fetch_and_compute_stokes())
            t1.start()
        else:
            print("\t bg calculation")
            self.fetch_and_compute_stokes()
            # self.fetch_and_compute_jones()

    def run_reconstruction_BG_correction(self, background : object, threaded = False):
        if threaded:
            t1 = threading.Thread(target=self.fetch_and_correct_background_and_recon_image(background))
            t1.start()
        else:
            print('\n Sample Reconstruction')
            self.fetch_and_correct_background_and_recon_image(background)


