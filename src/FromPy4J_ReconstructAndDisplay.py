#!/usr/bin/env python
# title           : ReconstructAndDisplay.py
# description     :Simple execution of Reconstruction Package
# author          :bryant.chhun
# date            :12/3/18
# version         :0.0
# usage           :from terminal: python ReconstructAndDisplay.py
# notes           :
# python_version  :3.6

"""
This code describes simple execution of Reconstruction and Visualization code.
    Data is received from Micromanager using mm2Python, is processed in this python package,
    and then is displayed in a viewer.
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.GUI.NapariWindowOverlay import NapariWindowOverlay
from src.DataPipe.PipeToReconOrder import PipeToReconOrder
from src.FileManagement.MonitorDatastores import MonitorDatastores
from src.DataPipe.PipeFromPy4j import PipeFromPy4j
from src.SignalController.SignalController import SignalController
from src.Processing.ReconOrder import ReconOrder
from py4j.java_gateway import JavaGateway

from napari_gui import Window, Viewer


if __name__ == '__main__':
    # starting
    application = QApplication(sys.argv)

    #create Viewer, Windows, gateway
    viewer = Viewer()
    win = Window(Viewer(), show=False)
    overlay_window = NapariWindowOverlay(win)
    gateway = JavaGateway()

    #initialize file loaders
    pipe = PipeFromPy4j()
    #loader_bg = PipeFromPy4j(flag)
    monitor = MonitorDatastores(gateway)

    #initialize processors
    processor = ReconOrder()
    processor.frames = 5
    # processor_bg = ReconOrder()
    # processor_bg.frames = 5

    #initialize SignalController
    signals = SignalController(processor)

    #Connections: Monitor to/from Pipeline
    monitor.make_connection(pipe)
    pipe.make_connection(monitor)

    #Connections: Pipeline to/from Processor
    pipe.set_processor(processor)
    # loader_bg.set_processor(processor_bg)

    #Connections: Pipeline to/from GUI
    overlay_window.make_connection(pipe)
    pipe.make_connection(overlay_window)

    #Connections: SignalController to/from GUI
    # for gui-initiated pipeline or processing events
    # such as averaging, adjusting line widths, etc.
    overlay_window.make_connection(signals)
    signals.make_connection(overlay_window)

    # BGprocess first
    # pipe_bg.run_reconstruction(threaded=False)
    # pipe.run_reconstruction_BG_correction(pipe.get_processor(), threaded=True)

    sys.exit(application.exec_())