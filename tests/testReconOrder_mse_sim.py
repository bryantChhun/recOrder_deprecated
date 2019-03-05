#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/12/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import unittest

import numpy as np

from src.DataPipe.PipeFromFiles import PipeFromFiles
from src.Processing.ReconOrder import ReconOrder
from tests.testUtils.testMetrics import mse


'''
Methods to check whether all IMAGE data in both raw and npy format are trainable
'''

class TestImageReconstruction(unittest.TestCase):

    targetData = "testData/reconData/simulated/"
    condition = "quarter_wave"

    target_ITrans = targetData + \
                         condition + \
                         "/transmission.npy"
    target_retard = targetData + \
                         condition + \
                         "/retardance.npy"
    target_Orientation = targetData + \
                         condition + \
                         "/slowaxis.npy"
    target_Scattering = targetData + \
                         condition + \
                         "/polarization.npy"

    def construct_all(self):
        # create file loaders
        datapipe = PipeFromFiles(type="Test", sample_type="Simulation1")

        # initialize processors
        self.processor = ReconOrder()
        self.processor.frames = 5

        datapipe.set_processor(self.processor)

        datapipe.compute_inst_matrix()

        # important: do not thread this
        # important: this does not background correct
        datapipe.run_reconstruction(threaded=False)

    def test_mse_Itrans(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.I_trans, np.load(self.target_ITrans)), 100)


    def test_mse_retard(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.retard, np.load(self.target_retard)), 100)


    def test_mse_orientation(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.azimuth, np.load(self.target_Orientation)), 100)


    def test_mse_scattering(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.scattering, np.load(self.target_Scattering)), 100)


if __name__ == '__main__':
    unittest.main()