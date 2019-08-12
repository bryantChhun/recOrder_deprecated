# bchhun, {2019-07-29}

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QWidget

from recOrder import BackgroundData
from recOrder.program.DataPipe.PipeFromFiles import PipeFromFiles
from recOrder.program.DataPipe.PipeFromPy4j import PipeFromPy4j
from recOrder.MicroscopeController.mm2python_controller import py4j_collect_background, py4j_snap_and_correct, py4j_monitor_LC
from .qtdesigner.ReconOrderUI import Ui_ReconOrderUI


class RecorderWindowControl(Ui_ReconOrderUI, QWidget):

    Background = None
    _gate = None

    window_update_signal = pyqtSignal(object)

    def __init__(self, win: QtWidgets, gateway=None):
        super(RecorderWindowControl, self).__init__()
        self.setupUi(win)

        self.qbutton_snap_and_correct.clicked[bool].connect(self.snap_and_correct)
        self.qbutton_collect_background.clicked[bool].connect(self.collect_background)
        self.qbutton_file_browser.clicked[bool].connect(self.file_browser)
        self.start_monitor.clicked[bool].connect(self.launch_monitor)
        # self.qbutton_calibrate_lc.clicked[bool].connect(self.calibrate_lc)
        # self.qline_bg_corr_path.editingFinished.connect(self.bg_corr_path_changed)
        # self.qline_swing.editingFinished.connect(self.swing_changed)
        # self.qline_wavelength.editingFinished.connect(self.wavelength_changed)

        self.gateway = gateway
        self.Background = BackgroundData()

    @property
    def gateway(self):
        return self._gate

    @gateway.setter
    def gateway(self, gateway):
        self._gate = gateway

    def assign_pipes(self, pipe, pipe_bg):
        if not isinstance(pipe, PipeFromFiles) and not isinstance(pipe_bg, PipeFromFiles) \
                and not isinstance(pipe, PipeFromPy4j) and not isinstance(pipe_bg, PipeFromPy4j):
            raise NotImplementedError("pipes must be of type PipeFromFiles or PipeFromPy4j")
        self.pipe = pipe
        self.pipe_bg = pipe_bg

    def openFileNameDialog(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return fileName

    @pyqtSlot(bool)
    def snap_and_correct(self):
        self.log_area.append("calling snap and correct")
        try:
            snap_bg_corr = py4j_snap_and_correct(self._gate, self.Background)
            if snap_bg_corr:
                self.window_update_signal.emit(snap_bg_corr)
        except Exception as ex:
            self.log_area.append("exception during snap and correct \n\t"+str(ex))
            print("exception during snap and correct \n\t"+str(ex))

    @pyqtSlot(bool)
    def collect_background(self):
        try:
            self.Background = py4j_collect_background(self._gate, self.Background)
            if self.Background is False or None:
                return None
            else:
                self.window_update_signal.emit(self.Background)
        except Exception as ex:
            print("exception during collect background \n\t"+str(ex))

    @pyqtSlot(bool)
    def launch_monitor(self):
        try:
            print("launching monitor")
            mlc = py4j_monitor_LC(self._gate, self.Background)
            mlc.launch_monitor()
        except Exception as ex:
            print("Exception during launch monitor \n\t"+str(ex))

    @pyqtSlot(bool)
    def file_browser(self):
        name = self.openFileNameDialog()
        self.qline_bg_corr_path.setText(name)

    @pyqtSlot()
    def bg_corr_path_changed(self):
        raise NotImplementedError

    @pyqtSlot(bool)
    def calibrate_lc(self):
        print("calibrate LC called")
        raise NotImplementedError

    @pyqtSlot()
    def swing_changed(self):
        print("swing changed")
        raise NotImplementedError

    @pyqtSlot()
    def wavelength_changed(self):
        print("wavelength changed")
        raise NotImplementedError
