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

from src.GUI.NapariWindowOverlay import NapariWindowOverlay
from src.DataPipe.PipeFromFiles import PipeFromFiles
from src.GUI.qtdesigner.ReconOrderUI import Ui_ReconOrderUI
from src.SignalController.SignalController import SignalController
from src.Processing.ReconOrder import ReconOrder
from py4j.java_gateway import JavaGateway

from napari import ViewerApp
from napari.util import app_context

if __name__ == '__main__':
    with app_context():

        gateway = JavaGateway()

        #create Viewer, Windows
        viewer = ViewerApp()
        overlay_window = NapariWindowOverlay(viewer)
        ReconOrderUI = QtWidgets.QDialog()
        ui = Ui_ReconOrderUI()
        ui.setupUi(ReconOrderUI)
        ui.gateway = gateway
        ReconOrderUI.show()

        #initialize file loaders
        loader = PipeFromFiles(type="Test", sample_type="Sample1")
        loader_bg = PipeFromFiles(type="Test", sample_type='BG')

        #initialize processors
        processor = ReconOrder()
        processor_bg = ReconOrder()

        #initialize SignalController
        signals = SignalController(processor)

        #Connections: Pipeline to/from Processor
        processor.frames = 5
        processor_bg.frames = 5
        loader.set_processor(processor)
        loader_bg.set_processor(processor_bg)

        #Connections: Pipeline to/from GUI
        overlay_window.make_connection(loader)
        loader.make_connection(overlay_window)

        #Connections: SignalController to/from GUI
        # for gui-initiated pipeline or processing events
        overlay_window.make_connection(signals)
        signals.make_connection(overlay_window)

        #Connections: recOrder to/from GUI
        overlay_window.make_connection(ui)

        # BGprocess first
        loader_bg.run_reconstruction(threaded=False)
        loader.run_reconstruction_BG_correction(loader_bg.background, threaded=True)



        #connect so button launches bgprocess
        ui.assign_pipes(loader, loader_bg)