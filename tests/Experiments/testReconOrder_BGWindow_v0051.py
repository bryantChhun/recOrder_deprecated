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

from src.GUI.NapariWindow import NapariWindow
from src.DataPipe.PipeFromFiles import PipeFromFiles
from src.Processing.ReconOrder import ReconOrder

if __name__ == '__main__':
    # starting
    application = QApplication(sys.argv)

    win = NapariWindow()

    #create file loaders
    loader = PipeFromFiles(type="Test", sample_type="Sample1")
    loader_bg = PipeFromFiles(type="Test", sample_type='BG')

    #initialize processors
    processor = ReconOrder()
    processor_bg = ReconOrder()

    processor.frames = 5
    processor_bg.frames = 5
    loader.set_processor(processor)
    loader_bg.set_processor(processor_bg)

    #Connections to GUI
    win.make_conection(loader)
    loader.make_connection(win)

    # BGprocess first
    loader_bg.run_reconstruction(threaded=False)
    loader.run_reconstruction_BG_correction(loader_bg.get_processor(), threaded=True)

    sys.exit(application.exec_())