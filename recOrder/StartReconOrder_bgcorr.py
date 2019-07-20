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

from PyQt5 import QtWidgets

from recOrder.visualize.GUI.NapariWindow import NapariWindow
from recOrder.program.DataPipe.PipeFromFiles import PipeFromFiles
from recOrder.visualize.GUI.RecorderWindowControl import RecorderWindowControl
from recOrder.program.SignalController.SignalController import SignalController
from recOrder.analyze.Processing.ReconOrder import ReconOrder
from py4j.java_gateway import JavaGateway
from recOrder.acquire.MicroscopeController.mm2python_controller import py4j_monitor_LC

from napari import ViewerApp
from napari.util import app_context

if __name__ == '__main__':
    with app_context():

        gateway = JavaGateway()

        #create Viewer, Windows
        viewer = ViewerApp()
        viewer_window = NapariWindow(viewer)

        recorder_window = QtWidgets.QDialog()
        recorder = RecorderWindowControl(recorder_window, gateway=gateway)
        recorder_window.show()

        #initialize file loaders
        loader = PipeFromFiles(type="Test", sample_type="Sample1")
        loader_bg = PipeFromFiles(type="Test", sample_type='BG')

        #initialize processors
        processor = ReconOrder()

        #initialize SignalController
        signals = SignalController()

        #Connections: Pipeline to/from Processor
        processor.frames = 5
        loader.set_processor(processor)
        loader_bg.set_processor(processor)

        #Connections: Pipeline to/from GUI
        signals.register(viewer_window)
        signals.register(recorder)
        signals.register(loader)
        signals.register(py4j_monitor_LC)
        signals.connect_signals()

        #Connections: SignalController to/from GUI
        # for gui-initiated pipeline or processing events
        # overlay_window.make_connection(signals)
        # signals.make_connection(overlay_window)

        #Connections: recOrder to/from GUI
        # viewer_window.make_connection(recorder)

        # BGprocess first
        loader_bg.run_reconstruction(threaded=False)
        loader.run_reconstruction_BG_correction(loader_bg.background, threaded=True)

        #connect so button launches bgprocess
        recorder.assign_pipes(loader, loader_bg)
