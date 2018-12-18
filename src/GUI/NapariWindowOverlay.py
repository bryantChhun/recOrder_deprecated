#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/6/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6


from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import numpy as np
import cv2

from src.FileManagement.RetrieveData import RetrieveData

from napari_gui.elements import Window

class NapariWindowOverlay(QWidget):

    debug = pyqtSignal(object)

    def __init__(self, type='Py4J'):
        super().__init__()

        # Data handling methods
        self.gate = None
        self.getfile = RetrieveData()
        self.type = type
        self.channels = ['Cy5', 'DAPI', 'FITC', 'Rhodamine']
        self.channels_reconOrder = ['State0', 'State1', 'State2', 'State3', 'State4']

        # UI initialization methods
        self.win = Window()
        self.viewer = self.win.add_viewer()

        self.meta = dict(name='3D1C', itype='mono')
        h, w = 2048, 2048
        self.init_data_1 = (65536 * 1 / 4) * np.zeros(shape=(h, w), dtype='uint16')
        self.init_data_2 = (65536 * 2 / 4) * np.zeros(shape=(h, w), dtype='uint16')
        self.init_data_3 = (65536 * 3 / 4) * np.zeros(shape=(h, w), dtype='uint16')
        self.init_data_4 = (65536 * 4 / 4) * np.zeros(shape=(h, w), dtype='uint16')

        self.layer1 = self.viewer.add_image(self.init_data_1, self.meta)
        self.layer1.cmap = 'grays'
        self.layer1.interpolation = 'spline36'
        self.layer1.clim = np.min(self.init_data_1), np.max(self.init_data_1)

        self.layer2 = self.viewer.add_image(self.init_data_2, self.meta)
        self.layer1.cmap = 'grays'
        self.layer2.interpolation = 'spline36'
        self.layer2.clim = np.min(self.init_data_2), np.max(self.init_data_2)

        self.layer3 = self.viewer.add_image(self.init_data_3, self.meta)
        self.layer1.cmap = 'grays'
        self.layer3.interpolation = 'spline36'
        self.layer3.clim = np.min(self.init_data_3), np.max(self.init_data_3)

        self.layer4 = self.viewer.add_image(self.init_data_4, self.meta)
        self.layer1.cmap = 'grays'
        self.layer4.interpolation = 'spline36'
        self.layer4.clim = np.min(self.init_data_4), np.max(self.init_data_4)

        self.win.show()

        self.layers = [self.layer1, self.layer2, self.layer3, self.layer4]

    def set_gateway(self, gateway):
        self.gate = gateway
        self.getfile.set_gateway(self.gate)

    def get_gateway(self):
        return self.gate

    @pyqtSlot(object)
    def update_layer_image(self, inst_reconOrder: object):
        self.win.show()
        self.layer1.image = inst_reconOrder.I_trans
        # cv2.imwrite('/Volumes/RAM_disk/trans_img.tif', np.ones(shape=(512,512), dtype=np.uint16))
        self.layer1.clim = np.min(inst_reconOrder.I_trans), np.max(inst_reconOrder.I_trans)
        self.debug.emit(np.max(self.layer1.image))

        self.layer2.image = inst_reconOrder.retard
        # cv2.imwrite('/Volumes/RAM_disk/retard_img.tif', inst_reconOrder.retard)
        self.layer2.clim = np.min(inst_reconOrder.retard), np.max(inst_reconOrder.retard)
        self.debug.emit(np.max(self.layer2.image))

        self.layer3.image = inst_reconOrder.scattering
        # cv2.imwrite('/Volumes/RAM_disk/azimuth_img.tif', inst_reconOrder.azimuth)
        self.layer3.clim = np.min(inst_reconOrder.azimuth), np.max(inst_reconOrder.azimuth)
        self.debug.emit(np.max(self.layer3.image))

        self.layer4.image = inst_reconOrder.azimuth_degree
        # cv2.imwrite('/Volumes/RAM_disk/polarization_img.tif', inst_reconOrder.polarization)
        self.layer4.clim = np.min(inst_reconOrder.polarization), np.max(inst_reconOrder.polarization)
        self.debug.emit(np.max(self.layer4.image))

    def make_conection(self, reconstruction):
        reconstruction.recon_complete.connect(self.update_layer_image)