# bchhun, {2019-08-14}

# framework imports
from recOrder.acquire.ReconOrderMonitor import ReconOrderMonitor
from recOrder.analyze.CalibrationAnalysis import CalibrationAnalysis
from recOrder.analyze.ReconstructOrder import ReconOrder
from recOrder.visualize.SimpleNapariWindow import SimpleNapariWindow
from recOrder.visualize.RecorderWindow import RecorderWindow
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from PyQt5 import QtWidgets
from py4j.java_gateway import JavaGateway


if __name__ == '__main__':

    gateway = JavaGateway()
    entry_point = gateway.entry_point
    mmc = gateway.entry_point.getCMMCore()

    # mmc.setProperty('MeadowlarkLcOpenSource', 'Wavelength', str(532))

    with napari.gui_qt():

        # acquire
        # create acquisition module for calibration
        mm_channels = ['State0', 'State1', 'State2', 'State3', 'State4']
        int_dat_channels = ['IExt', 'I90', 'I135', 'I45', 'I0']
        monitor = ReconOrderMonitor(mm_channels, int_dat_channels, gateway)

        # analyze
        calib = CalibrationAnalysis(gateway)
        ro = ReconOrder()
        # ro.swing = 0.03
        # ro.frames = 5


        # visualize
        # these visualization windows are fine
        viewer_window = SimpleNapariWindow(window_channel=1)
        recorder = QtWidgets.QDialog()
        recorder_window = RecorderWindow(recorder, gateway=gateway)

        program = Program(acquire=monitor,
                          analyze=calib,
                          visualize=viewer_window)
        program.add_module(recorder_window)

        program.build()

        # will launch the monitor.  let's let the button launch this instead
        # program.run()