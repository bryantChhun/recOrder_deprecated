#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :1/29/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable
import numpy as np

from src.FileManagement.MonitorDatastores import MonitorDatastores
from src.Processing.ReconOrder import ReconOrder


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class PipeFromPy4j(QObject):
    """
    Major difference from PipeFromPy4J versus the PipeFromFiles (for testing) is that
        PipeFromPy4J will spin off a thread upon pyqtSignal from data monitor
        Otherwise PipeFromPy4J does nothing and waits for signal
    Pipe emits signals to both window (ReconOrder object) and to Monitor (poll for new image data)
    Pipe receives signals from both window (update_complete) and from Monitor (image data)
    """

    recon_complete = pyqtSignal(object)
    poll_newdata = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._Recon = None
        self.recon_counter = 0
        self.background_processor = None

    @property
    def processor(self):
        return self._Recon

    @processor.setter
    def processor(self, processor):
        if isinstance(processor, ReconOrder):
            self._Recon = processor
        else:
            self._Recon = None
            raise NotImplementedError("Support only for Processor of type 'ReconOrder'")

    @pyqtSlot(tuple)
    def _fetch_images(self, memmap_path: tuple):
        """
        Slot to receive callbacks from the Monitor
        fetch_images both updates the underlying processor data and kicks off reconstruction threads
        :param memmap_path:
        :return:
        """
        print('fetching images from py4j')
        self._Recon.state = (memmap_path[0], np.memmap(memmap_path[1], dtype='uint16', offset=0, mode='r', shape=(1024,1024)))
        self.recon_counter += 1
        if self._Recon.frames == 4 and self.recon_counter == 4:
            self._kickoffRecon()
            self.recon_counter = 0
        elif self._Recon.frames == 5 and self.recon_counter ==5:
            self._kickoffRecon()
            self.recon_counter = 0
        elif self.recon_counter > 5:
            print("count mismanagement, resetting")
            self.recon_counter = 0

    @pyqtSlot(str)
    def _report_from_window(self, message: str):
        """
        Slot to receive callbacks from GUI
        Signals the data monitor to pull next data (or newest data?)
        :param message:
        :return:
        """
        print(message)
        self.poll_newdata.emit(True)

    # =========================  Core compute ===========================
    def _compute_stokes(self):
        print("compute stokes")
        self._Recon.compute_stokes()
        return True

    def _compute_inst_matrix(self):
        print("compute inst matrix")
        self._Recon.compute_inst_matrix()
        return True

    def _correct_background(self, background : object):
        print("correct background")
        self._Recon.correct_background(background)
        return True

    def _reconstruct_image(self):
        print("Reconstruct image")
        self._Recon.compute_physical()
        print("recon complete")
        self.recon_complete.emit(self._Recon)
        return True

    # ========================= Sequences of core compute ===============
    def _kickoffRecon(self):
        self.process = ProcessRunnable(target=self._compute_and_render, args=())
        self.process.start()

    def _compute_and_render(self):
        self._compute_stokes()
        if self.background_processor:
            self._correct_background(self.background_processor)
        self._reconstruct_image()

    # ========================= connect signals =========================

    def make_connection(self, event):
        from src.GUI.NapariWindow import NapariWindow
        if isinstance(event, NapariWindow):
            print("connecting window's signal to pipe's slot")
            event.update_complete.connect(self._report_from_window)
        elif isinstance(event, MonitorDatastores):
            print("connecting monitor's signal to pipe's slot")
            event.newImage.connect(self._fetch_images)




