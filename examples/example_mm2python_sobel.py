# bchhun, {2019-08-09}

"""
This code describes simple execution of Reconstruction and Visualization code.
    Data is received from Micromanager using mm2Python, is processed in this python package,
    and then is displayed in a viewer.
"""

# framework imports
from recOrder.acquire.MonitorPy4J import MonitorPy4j
from recOrder.analyze.sobel import Sobel
from recOrder.visualize.SimpleNapariWindow import SimpleNapariWindow
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from py4j.java_gateway import JavaGateway


if __name__ == '__main__':
    with napari.gui_qt():

        gateway = JavaGateway()

        # acquire
        acq = MonitorPy4j(gateway)

        # analyze
        sobel = Sobel()

        # visualize
        viewer_window = SimpleNapariWindow(window_channel=1)

        program = Program(acquire=acq,
                          analyze=sobel,
                          visualize=viewer_window)

        program.build()

        program.run()
