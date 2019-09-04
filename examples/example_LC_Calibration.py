# bchhun, {2019-08-09}

# framework imports
from recOrder.acquisition.MonitorPy4J import MonitorPy4j
from recOrder.analysis.CalibrationAnalysis import CalibrationAnalysis
from recOrder.visualization.SimpleNapariWindow import SimpleNapariWindow
from recOrder.visualization.RecorderWindow import RecorderWindow
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from PyQt5 import QtWidgets
from py4j.java_gateway import JavaGateway

"""
This example describes how to set up a recorder LC calibration window
"""
if __name__ == '__main__':

    gateway = JavaGateway()
    entry_point = gateway.entry_point
    mmc = gateway.entry_point.getCMMCore()

    # mmc.setProperty('MeadowlarkLcOpenSource', 'Wavelength', str(532))

    with napari.gui_qt():

        # acquisition
        # create acquisition module for calibration
        monitor = MonitorPy4j(gateway)

        # analysis
        calib = CalibrationAnalysis(gateway)

        # visualization
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
