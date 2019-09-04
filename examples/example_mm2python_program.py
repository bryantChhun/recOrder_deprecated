# bchhun, {2019-07-29}

"""
This code describes simple execution of Reconstruction and Visualization code.
    Data is received from Micromanager using mm2Python, is processed in this python package,
    and then is displayed in a viewer.
"""

# framework imports
from recOrder.acquisition.MonitorPy4J import MonitorPy4j
from recOrder.acquisition.ImplementPy4J import ImplementPy4J
from recOrder.visualization.SimpleNapariWindow import SimpleNapariWindow
from recOrder.visualization.RecorderWindow import RecorderWindow
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from PyQt5 import QtWidgets
from py4j.java_gateway import JavaGateway, GatewayParameters, CallbackServerParameters


if __name__ == '__main__':
    with napari.gui_qt():

        gateway = JavaGateway()

        # acquisition
        acq = MonitorPy4j()
        # acq = ImplementPy4J()

        # analysis


        # visualization
        viewer_window = SimpleNapariWindow()

        recorder = QtWidgets.QDialog()
        recorder_window = RecorderWindow(recorder, gateway=gateway)

        program = Program(acquire=acq,
                          visualize=viewer_window)
        program.add_module(recorder_window)

        program.build()

        program.run()
