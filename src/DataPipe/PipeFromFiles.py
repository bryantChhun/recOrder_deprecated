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

from src.DataStructures.BackgroundData import BackgroundData
from src.DataStructures.IntensityData import IntensityData
from src.DataStructures.PhysicalData import PhysicalData
from src.DataStructures.StokesData import StokesData
from src.FileManagement.RetrieveFiles import RetrieveData
from src.Processing.ReconOrder import ReconOrder
from src.Processing.VectorLayerUtils import compute_average, compute_length

from datetime import datetime

"""
PipeToReconOrder is a communication interface between data retrieval methods (under "FileManagement") 
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
        self.intensity = IntensityData()
        self.stokes = StokesData()
        self.physical = PhysicalData()
        self.background = BackgroundData()
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
        self.intensity.set_angle_from_index(0,
                                            self.retrieve_file.get_array_from_filename('State0',
                                                                                       type=self.type,
                                                                                       sample_type=self.sample_type))
        self.intensity.set_angle_from_index(1,
                                            self.retrieve_file.get_array_from_filename('State1',
                                                                                       type=self.type,
                                                                                       sample_type=self.sample_type))
        self.intensity.set_angle_from_index(2,
                                            self.retrieve_file.get_array_from_filename('State2',
                                                                                       type=self.type,
                                                                                       sample_type=self.sample_type))
        self.intensity.set_angle_from_index(3,
                                            self.retrieve_file.get_array_from_filename('State3',
                                                                                       type=self.type,
                                                                                       sample_type=self.sample_type))
        if self._Recon.frames == 5:
            self.intensity.set_angle_from_index(4,
                                                self.retrieve_file.get_array_from_filename('State4',
                                                                                           type=self.type,
                                                                                           sample_type=self.sample_type))
        self.intensity.print_none_vals()
        return True

    @timer
    def compute_stokes(self):
        print("compute stokes")
        self.stokes = self._Recon.compute_stokes(self.intensity)
        return True

    @timer
    def reconstruct_image(self):
        print("Reconstruct image")
        self.physical = self._Recon.compute_physical(self.stokes)
        return True

    @timer
    def rescale_bitdepth(self):
        print("rescaling bitdepth for display")
        self.physical = self._Recon.rescale_bitdepth(self.physical)
        return True

    @timer
    def compute_inst_matrix(self):
        print("compute inst matrix")
        self._Recon.compute_inst_matrix()
        return True

    @timer
    def correct_background(self, background : object):
        print("correct background")
        self._Recon.correct_background(self.stokes, background)
        return True

    # the lower two methods do not call the private recon attribute.
    def build_background(self):
        self.background.assign_intensity(self.intensity)
        self.background.assign_stokes(self.stokes)
        self.background.assign_physical(self.physical)

    def fetch_stokes_physical(self):
        print('fetch stokes physical')
        self.fetch_images()
        self.compute_inst_matrix()
        self.compute_stokes()
        self.reconstruct_image()
        self.build_background()

    def fetch_stokes_physical_bgcorr(self, background: BackgroundData):
        '''
        Performs both standard background correction from BG images AND
            local background correction using GaussianBlur
        :param background: ReconOrder object that contains stokes calculations for BG images
        :return: True if successful
        '''
        self.fetch_stokes_physical()
        self.correct_background(background)
        self.rescale_bitdepth()
        self.recon_complete.emit(self.physical)

    @pyqtSlot(list)
    def update_average(self, from_window: list):
        kernel = from_window[0]
        range_x = from_window[1]
        range_y = from_window[2]
        self.physical.azimuth_vector = compute_average(stk_img=self.stokes,
                                                       kernel=kernel,
                                                       range_x=range_x,
                                                       range_y=range_y,
                                                       func=self._Recon)
        self.recon_complete.emit(self.physical)

    def make_connection(self, window):
        window.average_change.connect(self.update_average)

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

    def run_reconstruction_BG_correction(self, background : BackgroundData, threaded = False):
        if threaded:
            self.process = ProcessRunnable(target=self.fetch_stokes_physical_bgcorr, args=(background,))
            self.process.start()
        else:
            print('\n Sample Reconstruction')
            self.fetch_stokes_physical_bgcorr(background)
