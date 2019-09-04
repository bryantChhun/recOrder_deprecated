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

from recOrder.program.DataPipe import PipeToReconOrder_ray
from recOrder.analysis.Processing import ReconOrder_ray
from tests.testUtils.testMetrics import mse

import ray

'''
Methods to check whether all IMAGE data in both raw and npy format are trainable
'''

class TestImageReconstruction(unittest.TestCase):

    ray.init(num_cpus=8, include_webui=False, ignore_reinit_error=True)

    # targetData = "./testData/reconData/2018_10_02_MouseBrainSlice/"
    targetData = "./testData/Processed/2018_10_02_MouseBrainSlice/"
    # condition = "SM_2018_1002_1633_1_BG_2018_1002_1625_1"
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
        datapipe = PipeToReconOrder_ray.remote(type="Test", sample_type="Sample")
        datapipe_bg = PipeToReconOrder_ray.remote(type="Test", sample_type='BG')
        # datapipe = PipeToReconOrder.remote(type="Test", sample_type="Sample")
        # datapipe_bg = PipeToReconOrder.remote(type="Test", sample_type='BG')

        # initialize processors
        self.processor = ReconOrder_ray.remote()
        self.processor_bg = ReconOrder_ray.remote()
        self.processor.set_frames.remote(5)
        self.processor_bg.set_frames.remote(5)
        datapipe.set_processor(self.processor)
        datapipe_bg.set_processor(self.processor_bg)

        # BGprocess first
        datapipe_bg.run_reconstruction()
        datapipe.run_reconstruction_BG_correction(datapipe_bg.get_processor())

    def test_mse_Itrans(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.I_trans.get(), cv2.imread(self.target_ITrans, -1)), 100000)

    def test_mse_retard(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.retard, cv2.imread(self.target_retard, -1)), 100000)

    def test_mse_orientation(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.azimuth_degree, cv2.imread(self.target_Orientation, -1)), 100000)

    def test_mse_scattering(self):
        self.construct_all()
        self.assertLessEqual(mse(self.processor.scattering, cv2.imread(self.target_Scattering, -1)), 100000)

if __name__ == '__main__':
    unittest.main()
