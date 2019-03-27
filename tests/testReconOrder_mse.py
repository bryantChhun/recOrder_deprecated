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

import cv2

from src.DataPipe.PipeFromFiles import PipeFromFiles
from src.Processing.ReconOrder import ReconOrder
from tests.testUtils.testMetrics import mse


'''
Methods to check whether all IMAGE data in both raw and npy format are trainable
'''

class TestImageReconstruction(unittest.TestCase):

    targetData = "./testData/reconData/2018_10_02_MouseBrainSlice/"
    condition = "SM_2018_1002_1633_1_BG_2018_1002_1625_1"

    target_ITrans = targetData + \
                         condition + \
                         "/img_Transmission_t000_p000_z000.tif"
    target_retard = targetData + \
                         condition + \
                         "/img_Retardance_t000_p000_z000.tif"
    target_Orientation = targetData + \
                         condition + \
                         "/img_Orientation_t000_p000_z000.tif"
    target_Scattering = targetData + \
                         condition + \
                         "/img_Scattering_t000_p000_z000.tif"

    def construct_all(self):
        # create file loaders
        self.datapipe = PipeFromFiles(type="Test", sample_type="Sample1")
        self.datapipe_bg = PipeFromFiles(type="Test", sample_type='BG')

        # initialize processors
        processor = ReconOrder()
        # self.processor_bg = ReconOrder()
        processor.frames = 5
        # self.processor_bg.frames = 5

        self.datapipe.set_processor(processor)
        self.datapipe_bg.set_processor(processor)
        # datapipe_bg.set_processor(processor_bg)

        self.datapipe.compute_inst_matrix()
        self.datapipe_bg.compute_inst_matrix()

        # BGprocess first
        self.datapipe_bg.run_reconstruction()
        self.datapipe.run_reconstruction_BG_correction(self.datapipe_bg.background)

    def construct_BG_only(self):
        datapipe_bg = PipeFromFiles(type="Test", sample_type='BG')
        processor_bg = ReconOrder()
        processor_bg.frames = 5
        processor_bg.compute_inst_matrix()
        datapipe_bg.set_processor(processor_bg)
        datapipe_bg.run_reconstruction()
        return datapipe_bg

    def test_mse_Itrans(self):
        self.construct_all()
        self.assertLessEqual(mse(self.datapipe.physical.I_trans, cv2.imread(self.target_ITrans, -1)), 100000)


    def test_mse_retard(self):
        self.construct_all()
        self.assertLessEqual(mse(self.datapipe.physical.retard, cv2.imread(self.target_retard, -1)), 100000)


    def test_mse_orientation(self):
        self.construct_all()
        self.assertLessEqual(mse(self.datapipe.physical.azimuth_degree, cv2.imread(self.target_Orientation, -1)), 100000)


    def test_mse_scattering(self):
        self.construct_all()
        self.assertLessEqual(mse(self.datapipe.physical.scattering, cv2.imread(self.target_Scattering, -1)), 100000)


    def test_mse_ReuseBackground(self):
        bg_pipe = self.construct_BG_only()
        datapipe1 = PipeFromFiles(type="Test", sample_type="Sample1")
        datapipe2 = PipeFromFiles(type="Test", sample_type="Sample2")
        processor = ReconOrder()
        processor.frames = 5

        processor.compute_inst_matrix()

        datapipe1.set_processor(processor)
        datapipe2.set_processor(processor)
        datapipe1.compute_inst_matrix()
        datapipe2.compute_inst_matrix()

        datapipe1.run_reconstruction_BG_correction(bg_pipe.background)
        datapipe2.run_reconstruction_BG_correction(bg_pipe.background)


if __name__ == '__main__':
    unittest.main()
