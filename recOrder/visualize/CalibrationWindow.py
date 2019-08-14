# bchhun, {2019-07-29}

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot

from ._visualize_base import VisualizeBase
from .qtdesigner.ReconOrderUI import Ui_ReconOrderUI
from recOrder.microscope.mm2python_simple import snap_and_get_image


class CalibrationWindow(VisualizeBase, Ui_ReconOrderUI):

    def __init__(self, win: QtWidgets, gateway=None):
        super(CalibrationWindow, self).__init__()

        self.setupUi(win)

        # button's signals
        self.qbutton_snap_and_correct.clicked[bool].connect(self.snap)
        self.start_monitor.clicked[bool].connect(self.launch_monitor)
        self.qbutton_calibrate_lc.clicked[bool].connect(self.calibrate)

        self.gate = gateway

        self.gate.entry_point.clearQueue()

        # some params
        self.lc_bound = 0.02
        self.swing = 0.03
        self.I_black = 100
        self.wavelength = 532

        win.show()

    # runtime decoration of snap
    @VisualizeBase.emitter(channel=1)
    @pyqtSlot(bool)
    # because pyqtslot sends another parameter: bool, we need *args
    def snap(self, *args):
        try:
            data = snap_and_get_image(self.gate.entry_point, self.gate.getStudio())
            return data
        except Exception as ex:
            print("exception during snap\n\t"+str(ex))

    @VisualizeBase.emitter(channel=0)
    @pyqtSlot(bool)
    def launch_monitor(self, *args):
        # try:
        #     print("launching monitor")
        # except Exception as ex:
        #     print("Exception during launch monitor \n\t"+str(ex))
        pass

    @VisualizeBase.emitter(channel=20)
    def calibrate(self, *args):
        return [self.swing, self.wavelength, self.lc_bound, self.I_black]

    @VisualizeBase.receiver(channel=10)
    def le_state0(self, lc):
        self.le_state0_lca.setText(str(lc[0]))
        self.le_state0_lcb.setText(str(lc[1]))

    @VisualizeBase.receiver(channel=11)
    def le_state1(self, lc):
        self.le_state1_lca.setText(str(lc[0]))
        self.le_state1_lcb.setText(str(lc[1]))

    @VisualizeBase.receiver(channel=12)
    def le_state2(self, lc):
        self.le_state2_lca.setText(str(lc[0]))
        self.le_state2_lcb.setText(str(lc[1]))

    @VisualizeBase.receiver(channel=13)
    def le_state3(self, lc):
        self.le_state3_lca.setText(str(lc[0]))
        self.le_state3_lcb.setText(str(lc[1]))

    @VisualizeBase.receiver(channel=14)
    def le_state4(self, lc):
        self.le_state4_lca.setText(str(lc[0]))
        self.le_state4_lcb.setText(str(lc[1]))

