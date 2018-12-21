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

import ray


@ray.remote
class PipeToReconOrder_ray(object):

    def __init__(self,  type = "Test", sample_type = "Sample"):
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
            return False

    def get_processor(self):
        return self._Recon

    def fetch_images(self):
        start = datetime.now()

        self._Recon.set_state(0, self.retrieve_file.get_array_from_filename('State0', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(1, self.retrieve_file.get_array_from_filename('State1', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(2, self.retrieve_file.get_array_from_filename('State2', type=self.type, sample_type=self.sample_type))
        self._Recon.set_state(3, self.retrieve_file.get_array_from_filename('State3', type=self.type, sample_type=self.sample_type))
        if self._Recon.frames() == 5:
            self._Recon.set_state(4, self.retrieve_file.get_array_from_filename('State3', type=self.type,
                                                                                sample_type=self.sample_type))
        stop = datetime.now()
        print("fetch images = " + str((stop - start).microseconds))
        return True

    #todo: could probably move these to a more appropriate class
    def compute_stokes(self, remote = False):
        start = datetime.now()
        if remote:
            print('remote flag for stokes')
            self._Recon.compute_stokes.remote()
        else:
            print('no remote flag for stokes')
            self._Recon.compute_stokes(remote)
        stop = datetime.now()
        print("compute stokes = " + str((stop - start).microseconds))
        return True

    def compute_jones(self):
        start = datetime.now()
        self._Recon.compute_jones()
        stop = datetime.now()
        print("compute jones = " + str((stop - start).microseconds))
        return True

    def correct_background(self, background : object):
        start = datetime.now()

        self._Recon.correct_background(background)

        stop = datetime.now()
        print("correct background = " + str((stop - start).microseconds))
        return True

    def correct_background_localGauss(self):
        start = datetime.now()

        self._Recon.correct_background_localGauss()

        stop = datetime.now()
        print("correct background local gauss = " + str((stop - start).microseconds))
        return True

    def reconstruct_image(self):
        start = datetime.now()

        self._Recon.reconstruct_img()

        stop = datetime.now()
        print("Reconstruct image = " + str((stop - start).microseconds) +"\n")
        self.recon_complete.emit(self._Recon)
        return True

    def fetch_and_compute_stokes(self, remote=False):
        self.fetch_images()
        self.compute_stokes(remote)

    def fetch_and_compute_jones(self):
        self.fetch_images()
        self.compute_jones()

    def fetch_and_correct_background_and_recon_image(self, background: object, remote = False):
        '''
        Performs both standard background correction from BG images AND
            local background correction using GaussianBlur
        :param background: ReconOrder object that contains stokes calculations for BG images
        :return: True if successful
        '''
        self.fetch_images()
        self.compute_stokes(remote=remote)
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


    #Todo: remove or think again about how to multi thread processing.  could call static executor
    def run_reconstruction(self, threaded = False, remote=False):
        '''
        This recon is used to rebuild background files.  Sample files will also call reconstruct_image

        :param threaded:
        :return:
        '''
        if threaded:
            t1 = threading.Thread(target=self.fetch_and_compute_stokes(remote=remote))
            t1.start()
        else:
            print("bg calculation")
            self.fetch_and_compute_stokes(remote=remote)
            # self.fetch_and_compute_jones()

    def run_BGCorrTest_reconstruction(self, background : object, threaded = False, remote = False):
        if threaded:
            t1 = threading.Thread(target=self.fetch_and_correct_background_and_recon_image(background, remote=remote))
            t1.start()
        else:
            self.fetch_and_correct_background_and_recon_image(background, remote=remote)