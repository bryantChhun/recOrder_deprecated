# bchhun, {2019-07-29}

"""
This code describes simple execution of Reconstruction and Visualization code.
    Data is received from Micromanager using mm2Python, is processed in this python package,
    and then is displayed in a viewer.
"""

# framework imports
from recOrder.visualization.SimpleNapariWindow import SimpleNapariWindow
from recOrder.visualization.RecorderWindow import RecorderWindow
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from PyQt5 import QtWidgets
from py4j.java_gateway import JavaGateway


if __name__ == '__main__':
    with napari.gui_qt():

        gateway = JavaGateway()

        # acquisition

        # analysis

        # visualization
        viewer_window = SimpleNapariWindow(window_channel=4)

        recorder = QtWidgets.QDialog()
        recorder_window = RecorderWindow(recorder, gateway=gateway)

        program = Program(visualize=viewer_window)
        program.add_module(recorder_window)

        program.build()

        program.run()
