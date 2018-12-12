#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/12/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from sklearn.metrics import mean_squared_error
import sys
from PyQt5.QtWidgets import QApplication

from src.DataPipe.StreamDataToProcessor import LoadFromFiles
from src.Processing.ReconOrder import ReconOrder

import unittest
#
# class TestImageData(unittest.TestCase):
#

if __name__ == '__main__':
    # starting
    application = QApplication(sys.argv)

    processor = ReconOrder()
    processor.set_frames(5)

    loader = LoadFromFiles(processor, type="Test", sample_type="Sample")

    loader.fetch_and_compute_test_images()

    im0 = processor.I_trans
    im1 = processor.retard
    im2 = processor.scattering
    im3 = processor.azimuth_degree

    sys.exit(application.exec_())