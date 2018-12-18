#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/4/18
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
    loader = PipeToReconOrder(type="Test", sample_type="Sample")
    loader_bg = PipeToReconOrder(type="Test", sample_type='BG')
    processor = ReconOrder()

    processor.set_frames(5)
    win.make_conection(loader)
    loader.make_connection(win)

    loader.run_test_reconstruction()

    sys.exit(application.exec_())