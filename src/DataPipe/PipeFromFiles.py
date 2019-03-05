#!/usr/bin/env python
# title           : PipeFromFiles.py
# description     :
# author          :bryant.chhun
# date            :12/4/18
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable

from src.FileManagement.RetrieveFiles import RetrieveData
from src.Processing.ReconOrder import ReconOrder

from datetime import datetime

"""
PipeToReconOrder is a communication interface between data retrieval methods (under "FileManagement") 
    and 
"""


def timer(func):
    def timer_wrap(*args, **kwargs):
        start = datetime.now()
        func(*args,**kwargs)
        stop = datetime.now()
        print("\t"+str((stop-start).microseconds))
    return timer_wrap


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class PipeFromFiles(QObject):

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
        self._Recon.state = (0, self.retrieve_file.get_array_from_filename('State0', type=self.type, sample_type=self.sample_type))
        self._Recon.state = (1, self.retrieve_file.get_array_from_filename('State1', type=self.type, sample_type=self.sample_type))
        self._Recon.state = (2, self.retrieve_file.get_array_from_filename('State2', type=self.type, sample_type=self.sample_type))
        self._Recon.state = (3, self.retrieve_file.get_array_from_filename('State3', type=self.type, sample_type=self.sample_type))
        if self._Recon.frames == 5:
            self._Recon.state = (4, self.retrieve_file.get_array_from_filename('State4', type=self.type,
                                                                                sample_type=self.sample_type))
        return True

    @timer
    def compute_stokes(self):
        print("compute stokes")
        self._Recon.compute_stokes()
        return True

    @timer
    def reconstruct_image(self):
        print("Reconstruct image")
        self._Recon.compute_physical()
        self.recon_complete.emit(self._Recon)
        return True

    @timer
    def rescale_bitdepth(self):
        print("rescaling bitdepth for display")
        self._Recon.rescale_bitdepth()
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

    def fetch_stokes_physical(self):
        print('fetch stokes physical')
        self.fetch_images()
        self.compute_stokes()
        self.reconstruct_image()

    def fetch_stokes_physical_bgcorr(self, background: object):
        '''
        Performs both standard background correction from BG images AND
            local background correction using GaussianBlur
        :param background: ReconOrder object that contains stokes calculations for BG images
        :return: True if successful
        '''
        self.fetch_stokes_physical()
        self.correct_background(background)
        self.rescale_bitdepth()

    # to receive callbacks from GUI
    @pyqtSlot(str)
    def report_from_window(self, message: str):
        print(message)

    def make_connection(self, window):
        window.update_complete.connect(self.report_from_window)

    '''
    Threads for running reconstruction.  Needed to prevent blocking UI.
        Pyqt slots/signals will notify UI that data is ready.
    '''
    def run_reconstruction(self, threaded = False):
        if threaded:
            print('starting thread')
            self.process = ProcessRunnable(target=self.fetch_stokes_physical, args=())
            self.process.start()
        else:
            print("\t bg calculation")
            self.fetch_stokes_physical()

    def run_reconstruction_BG_correction(self, background : object, threaded = False):
        if threaded:
            self.process = ProcessRunnable(target=self.fetch_stokes_physical_bgcorr, args=(background,))
            self.process.start()
        else:
            print('\n Sample Reconstruction')
            self.fetch_stokes_physical_bgcorr(background)
