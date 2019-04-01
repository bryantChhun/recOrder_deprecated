# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReconOrderUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QWidget, QDesktopWidget
from src.DataPipe.PipeFromFiles import PipeFromFiles
from src.DataPipe.PipeFromPy4j import PipeFromPy4j
from src.MicroscopeController.Py4jController import *


class Ui_ReconOrderUI(QWidget):

    Background = None
    _gate = None

    window_update_signal = pyqtSignal(object)

    def setupUi(self, ReconOrderUI):
        ReconOrderUI.setObjectName("ReconOrderUI")
        ReconOrderUI.resize(500, 229)
        self.tabWidget = QtWidgets.QTabWidget(ReconOrderUI)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 481, 211))
        self.tabWidget.setObjectName("tabWidget")
        self.main_tab = QtWidgets.QWidget()
        self.main_tab.setObjectName("main_tab")
        self.qbutton_snap_and_correct = QtWidgets.QPushButton(self.main_tab)
        self.qbutton_snap_and_correct.setGeometry(QtCore.QRect(10, 10, 160, 80))
        self.qbutton_snap_and_correct.setAutoDefault(False)
        self.qbutton_snap_and_correct.setObjectName("snap_and_correct")
        self.qbutton_collect_background = QtWidgets.QPushButton(self.main_tab)
        self.qbutton_collect_background.setGeometry(QtCore.QRect(300, 10, 160, 80))
        self.qbutton_collect_background.setAutoDefault(False)
        self.qbutton_collect_background.setObjectName("collect_background")
        self.qbutton_file_browser = QtWidgets.QPushButton(self.main_tab)
        self.qbutton_file_browser.setGeometry(QtCore.QRect(340, 110, 113, 32))
        self.qbutton_file_browser.setObjectName("file_browser")
        self._qlabel_bg_corr_label = QtWidgets.QLabel(self.main_tab)
        self._qlabel_bg_corr_label.setGeometry(QtCore.QRect(10, 120, 171, 16))
        self._qlabel_bg_corr_label.setObjectName("bg_corr_label")
        self.qline_bg_corr_path = QtWidgets.QLineEdit(self.main_tab)
        self.qline_bg_corr_path.setGeometry(QtCore.QRect(10, 140, 451, 21))
        self.qline_bg_corr_path.setObjectName("qline_bg_corr_path")
        self.tabWidget.addTab(self.main_tab, "")
        self.calibrate_lc_tab = QtWidgets.QWidget()
        self.calibrate_lc_tab.setObjectName("calibrate_lc_tab")
        self.qbutton_calibrate_lc = QtWidgets.QPushButton(self.calibrate_lc_tab)
        self.qbutton_calibrate_lc.setGeometry(QtCore.QRect(160, 10, 160, 80))
        self.qbutton_calibrate_lc.setAutoDefault(False)
        self.qbutton_calibrate_lc.setObjectName("calibrate_lc")
        self.qline_swing = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.qline_swing.setGeometry(QtCore.QRect(20, 130, 113, 21))
        self.qline_swing.setObjectName("qline_swing")
        self.qline_wavelength = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.qline_wavelength.setGeometry(QtCore.QRect(340, 130, 113, 21))
        self.qline_wavelength.setObjectName("qline_wavelength")
        self._qlabel_swing = QtWidgets.QLabel(self.calibrate_lc_tab)
        self._qlabel_swing.setGeometry(QtCore.QRect(20, 110, 60, 16))
        self._qlabel_swing.setObjectName("qlabel_swing")
        self._qlabel_wavelength = QtWidgets.QLabel(self.calibrate_lc_tab)
        self._qlabel_wavelength.setGeometry(QtCore.QRect(340, 110, 81, 16))
        self._qlabel_wavelength.setObjectName("qlabel_wavelength")
        self.tabWidget.addTab(self.calibrate_lc_tab, "")

        self.retranslateUi(ReconOrderUI)
        self.tabWidget.setCurrentIndex(0)

        self.qbutton_snap_and_correct.clicked[bool].connect(self.snap_and_correct)
        self.qbutton_collect_background.clicked[bool].connect(self.collect_background)
        self.qbutton_file_browser.clicked[bool].connect(self.file_browser)
        self.qbutton_calibrate_lc.clicked[bool].connect(self.calibrate_lc)
        self.qline_bg_corr_path.editingFinished.connect(self.bg_corr_path_changed)
        self.qline_swing.editingFinished.connect(self.swing_changed)
        self.qline_wavelength.editingFinished.connect(self.wavelength_changed)
        # QtCore.QMetaObject.connectSlotsByName(ReconOrderUI)

        self._gate = None
        self.Background = BackgroundData()

        # move the windows apart!
        # cp = QDesktopWidget().availableGeometry().center()
        # geo = self.geometry()
        # x, y = geo.x(), geo.y()
        # x.
        # self.move(x+1000,y)

    @property
    def gateway(self):
        return self._gate

    @gateway.setter
    def gateway(self, gateway_):
        self._gate = gateway_

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
            print(fileName)
            self.qline_bg_corr_path.setText(fileName)

    # Py4J Controller calls
    @pyqtSlot(bool)
    def snap_and_correct(self):
        print("snap and correct background called")
        #snap_bg_corr is an object of type PhysicalData
        snap_bg_corr = py4j_snap_and_correct(self._gate, self.Background)
        print("emitting signal")
        self.window_update_signal.emit(snap_bg_corr)

    @pyqtSlot(bool)
    def collect_background(self):
        print("collect background called")
        self.Background = py4j_collect_background(self._gate, self.Background)
        if self.Background is False or None:
            return None
        else:
            self.window_update_signal.emit(self.Background)

    @pyqtSlot(bool)
    def file_browser(self):
        print("file browser called")
        self.openFileNameDialog()

    @pyqtSlot()
    def bg_corr_path_changed(self):
        print("bg correction path changed")
        # raise NotImplementedError

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

    def retranslateUi(self, ReconOrderUI):
        _translate = QtCore.QCoreApplication.translate
        ReconOrderUI.setWindowTitle(_translate("ReconOrderUI", "ReconOrder"))
        self.qbutton_snap_and_correct.setText(_translate("ReconOrderUI", "Snap and BG Correct"))
        self.qbutton_collect_background.setText(_translate("ReconOrderUI", "Collect Background"))
        self.qbutton_file_browser.setText(_translate("ReconOrderUI", "Browse"))
        self._qlabel_bg_corr_label.setText(_translate("ReconOrderUI", "Background correction file"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.main_tab), _translate("ReconOrderUI", "Snap and BG"))
        self.qbutton_calibrate_lc.setText(_translate("ReconOrderUI", "Calibrate LC"))
        self.qline_swing.setText(_translate("ReconOrderUI", "0.03"))
        self.qline_wavelength.setText(_translate("ReconOrderUI", "532"))
        self._qlabel_swing.setText(_translate("ReconOrderUI", "Swing"))
        self._qlabel_wavelength.setText(_translate("ReconOrderUI", "Wavelength"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calibrate_lc_tab), _translate("ReconOrderUI", "Calibrate LC"))

#for testing
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ReconOrderUI = QtWidgets.QDialog()
    ui = Ui_ReconOrderUI()
    ui.setupUi(ReconOrderUI)
    ReconOrderUI.show()
    sys.exit(app.exec_())

