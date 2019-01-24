#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/12/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import sys
from PyQt5.QtWidgets import QApplication

from src.GUI.NapariWindowOverlay_v0051 import NapariWindowOverlay
from src.DataPipe.PipeToReconOrder import PipeToReconOrder
from src.DataPipe.SignalController import SignalController
from src.Processing.ReconOrder import ReconOrder

from napari_gui import Window, Viewer

if __name__ == '__main__':
    # starting
    application = QApplication(sys.argv)

    #create Viewer, Windows
    viewer = Viewer()
    win = Window(Viewer(), show=False)
    overlay_window = NapariWindowOverlay(win)

    #initialize file loaders
    loader = PipeToReconOrder(type="Test", sample_type="Sample1")
    loader_bg = PipeToReconOrder(type="Test", sample_type='BG')

    #initialize processors
    processor = ReconOrder()
    processor_bg = ReconOrder()
    processor_localGauss = ReconOrder()

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

    # BGprocess first
    loader_bg.run_reconstruction(threaded=False)
    loader.run_reconstruction_BG_correction(loader_bg.get_processor(), threaded=True)

    sys.exit(application.exec_())