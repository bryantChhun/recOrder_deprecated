# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReconOrderUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ReconOrderUI(object):
    def setupUi(self, ReconOrderUI):
        ReconOrderUI.setObjectName("ReconOrderUI")
        ReconOrderUI.resize(500, 423)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReconOrderUI.sizePolicy().hasHeightForWidth())
        ReconOrderUI.setSizePolicy(sizePolicy)
        self.tabWidget = QtWidgets.QTabWidget(ReconOrderUI)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 481, 401))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.main_tab = QtWidgets.QWidget()
        self.main_tab.setObjectName("main_tab")
        self.qbutton_snap_and_correct = QtWidgets.QPushButton(self.main_tab)
        self.qbutton_snap_and_correct.setGeometry(QtCore.QRect(10, 10, 160, 80))
        self.qbutton_snap_and_correct.setAutoDefault(False)
        self.qbutton_snap_and_correct.setObjectName("qbutton_snap_and_correct")
        self.qbutton_collect_background = QtWidgets.QPushButton(self.main_tab)
        self.qbutton_collect_background.setGeometry(QtCore.QRect(300, 10, 160, 80))
        self.qbutton_collect_background.setAutoDefault(False)
        self.qbutton_collect_background.setObjectName("qbutton_collect_background")
        self.qbutton_file_browser = QtWidgets.QPushButton(self.main_tab)
        self.qbutton_file_browser.setGeometry(QtCore.QRect(340, 110, 113, 32))
        self.qbutton_file_browser.setObjectName("qbutton_file_browser")
        self._qlabel_bg_corr_label = QtWidgets.QLabel(self.main_tab)
        self._qlabel_bg_corr_label.setGeometry(QtCore.QRect(10, 120, 171, 16))
        self._qlabel_bg_corr_label.setObjectName("_qlabel_bg_corr_label")
        self.qline_bg_corr_path = QtWidgets.QLineEdit(self.main_tab)
        self.qline_bg_corr_path.setGeometry(QtCore.QRect(10, 140, 451, 21))
        self.qline_bg_corr_path.setObjectName("qline_bg_corr_path")
        self.start_monitor = QtWidgets.QPushButton(self.main_tab)
        self.start_monitor.setGeometry(QtCore.QRect(130, 190, 211, 101))
        self.start_monitor.setObjectName("start_monitor")
        self.tabWidget.addTab(self.main_tab, "")
        self.calibrate_lc_tab = QtWidgets.QWidget()
        self.calibrate_lc_tab.setObjectName("calibrate_lc_tab")
        self.qbutton_calibrate_lc = QtWidgets.QPushButton(self.calibrate_lc_tab)
        self.qbutton_calibrate_lc.setGeometry(QtCore.QRect(160, 10, 160, 80))
        self.qbutton_calibrate_lc.setAutoDefault(False)
        self.qbutton_calibrate_lc.setObjectName("qbutton_calibrate_lc")
        self.qline_swing = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.qline_swing.setGeometry(QtCore.QRect(20, 120, 113, 21))
        self.qline_swing.setObjectName("qline_swing")
        self.qline_wavelength = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.qline_wavelength.setGeometry(QtCore.QRect(340, 120, 113, 21))
        self.qline_wavelength.setObjectName("qline_wavelength")
        self._qlabel_swing = QtWidgets.QLabel(self.calibrate_lc_tab)
        self._qlabel_swing.setGeometry(QtCore.QRect(20, 100, 60, 16))
        self._qlabel_swing.setObjectName("_qlabel_swing")
        self._qlabel_wavelength = QtWidgets.QLabel(self.calibrate_lc_tab)
        self._qlabel_wavelength.setGeometry(QtCore.QRect(340, 100, 81, 16))
        self._qlabel_wavelength.setObjectName("_qlabel_wavelength")
        self.label = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label.setGeometry(QtCore.QRect(20, 190, 60, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label_2.setGeometry(QtCore.QRect(20, 220, 60, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label_3.setGeometry(QtCore.QRect(20, 250, 60, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label_4.setGeometry(QtCore.QRect(20, 280, 60, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label_5.setGeometry(QtCore.QRect(20, 310, 60, 16))
        self.label_5.setObjectName("label_5")
        self.le_state0_lca = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state0_lca.setGeometry(QtCore.QRect(80, 190, 61, 21))
        self.le_state0_lca.setObjectName("le_state0_lca")
        self.le_state0_lcb = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state0_lcb.setGeometry(QtCore.QRect(160, 190, 61, 21))
        self.le_state0_lcb.setObjectName("le_state0_lcb")
        self.le_state1_lca = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state1_lca.setGeometry(QtCore.QRect(80, 220, 61, 21))
        self.le_state1_lca.setObjectName("le_state1_lca")
        self.le_state1_lcb = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state1_lcb.setGeometry(QtCore.QRect(160, 220, 61, 21))
        self.le_state1_lcb.setObjectName("le_state1_lcb")
        self.le_state2_lca = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state2_lca.setGeometry(QtCore.QRect(80, 250, 61, 21))
        self.le_state2_lca.setObjectName("le_state2_lca")
        self.le_state2_lcb = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state2_lcb.setGeometry(QtCore.QRect(160, 250, 61, 21))
        self.le_state2_lcb.setObjectName("le_state2_lcb")
        self.le_state3_lca = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state3_lca.setGeometry(QtCore.QRect(80, 280, 61, 21))
        self.le_state3_lca.setObjectName("le_state3_lca")
        self.le_state3_lcb = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state3_lcb.setGeometry(QtCore.QRect(160, 280, 61, 21))
        self.le_state3_lcb.setObjectName("le_state3_lcb")
        self.le_state4_lca = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state4_lca.setGeometry(QtCore.QRect(80, 310, 61, 21))
        self.le_state4_lca.setObjectName("le_state4_lca")
        self.le_state4_lcb = QtWidgets.QLineEdit(self.calibrate_lc_tab)
        self.le_state4_lcb.setGeometry(QtCore.QRect(160, 310, 61, 21))
        self.le_state4_lcb.setObjectName("le_state4_lcb")
        self.label_6 = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label_6.setGeometry(QtCore.QRect(80, 170, 60, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.calibrate_lc_tab)
        self.label_7.setGeometry(QtCore.QRect(160, 170, 60, 16))
        self.label_7.setObjectName("label_7")
        self.tabWidget.addTab(self.calibrate_lc_tab, "")
        self.logs = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logs.sizePolicy().hasHeightForWidth())
        self.logs.setSizePolicy(sizePolicy)
        self.logs.setObjectName("logs")
        self.scrollArea = QtWidgets.QScrollArea(self.logs)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 481, 371))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 479, 369))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.log_area = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.log_area.setGeometry(QtCore.QRect(0, 0, 481, 371))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.log_area.setFont(font)
        self.log_area.setAcceptDrops(False)
        self.log_area.setObjectName("log_area")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.logs, "")

        self.retranslateUi(ReconOrderUI)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ReconOrderUI)

    def retranslateUi(self, ReconOrderUI):
        _translate = QtCore.QCoreApplication.translate
        ReconOrderUI.setWindowTitle(_translate("ReconOrderUI", "ReconOrder"))
        self.qbutton_snap_and_correct.setText(_translate("ReconOrderUI", "Snap and BG Correct"))
        self.qbutton_collect_background.setText(_translate("ReconOrderUI", "Collect Background"))
        self.qbutton_file_browser.setText(_translate("ReconOrderUI", "Browse"))
        self._qlabel_bg_corr_label.setText(_translate("ReconOrderUI", "Background correction file"))
        self.start_monitor.setText(_translate("ReconOrderUI", "Monitor and reconstruct"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.main_tab), _translate("ReconOrderUI", "Snap and BG"))
        self.qbutton_calibrate_lc.setText(_translate("ReconOrderUI", "Calibrate LC"))
        self.qline_swing.setText(_translate("ReconOrderUI", "0.03"))
        self.qline_wavelength.setText(_translate("ReconOrderUI", "532"))
        self._qlabel_swing.setText(_translate("ReconOrderUI", "Swing"))
        self._qlabel_wavelength.setText(_translate("ReconOrderUI", "Wavelength"))
        self.label.setText(_translate("ReconOrderUI", "State 0"))
        self.label_2.setText(_translate("ReconOrderUI", "State 1"))
        self.label_3.setText(_translate("ReconOrderUI", "State 2"))
        self.label_4.setText(_translate("ReconOrderUI", "State 3"))
        self.label_5.setText(_translate("ReconOrderUI", "State 4"))
        self.label_6.setText(_translate("ReconOrderUI", "LCA"))
        self.label_7.setText(_translate("ReconOrderUI", "LCB"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calibrate_lc_tab), _translate("ReconOrderUI", "Calibrate LC"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.logs), _translate("ReconOrderUI", "logs"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ReconOrderUI = QtWidgets.QDialog()
    ui = Ui_ReconOrderUI()
    ui.setupUi(ReconOrderUI)
    ReconOrderUI.show()
    sys.exit(app.exec_())
