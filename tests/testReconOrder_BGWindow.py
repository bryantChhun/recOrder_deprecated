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

from src.GUI.NapariWindowOverlay import NapariWindowOverlay
from src.DataPipe.PipeToReconOrder import PipeToReconOrder
from src.Processing.ReconOrder import ReconOrder

if __name__ == '__main__':
    # starting
    application = QApplication(sys.argv)

    win = NapariWindowOverlay()

    #create file loaders
    loader = PipeToReconOrder(type="Test", sample_type="Sample")
    loader_bg = PipeToReconOrder(type="Test", sample_type='BG')

    #initialize processors
    processor = ReconOrder()
    processor_bg = ReconOrder()
    processor_localGauss = ReconOrder()

    processor.set_frames(5)
    processor_bg.set_frames(5)
    loader.set_processor(processor)
    loader_bg.set_processor(processor_bg)

    #Connections to GUI
    win.make_conection(loader)
    loader.make_connection(win)

    # BGprocess first
    loader_bg.run_reconstruction(threaded=True)
    loader.run_BGCorrTest_reconstruction(loader_bg.get_processor(), threaded=True)

    sys.exit(application.exec_())