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

from src.FileManagement.RetrieveFiles import RetrieveData
from src.DataStructures.PhysicalData import PhysicalData
from src.Processing.ReconOrder import ReconOrder
from src.Processing import compute_average, convert_to_vector


class NapariWindowOverlay(QWidget):

    average_change = pyqtSignal(object)
    length_change = pyqtSignal(object)
    update_complete = pyqtSignal(str)

    def __init__(self, viewer, type='Py4J'):
        super().__init__()

        # Data handling methods
        self.gate = None
        self.getfile = RetrieveData()
        self.type = type
        self.channels = ['Cy5', 'DAPI', 'FITC', 'Rhodamine']
        self.channels_reconOrder = ['State0', 'State1', 'State2', 'State3', 'State4']

        # UI initialization methods
        self.viewer = viewer

        #init image data
        self.init_data_1 = 2**16 * np.random.rand(512,512)

        #init vector data
        N = 1028
        self.pos = np.zeros((N, N, 2), dtype=np.float32)
        dim = np.linspace(0, N - 1, N)
        xv, yv = np.meshgrid(dim, dim)
        self.pos[:, :, 0] = xv
        self.pos[:, :, 1] = yv

        #init layers with vector data and subscribe to gui notifications
        self.layer1 = self.viewer.add_vectors(self.pos)
        # self.layer1._default_avg = compute_average
        # self.layer1.length_bind_to(self.compute_length)
        self.layer2 = self.viewer.add_image(self.init_data_1, {})
        self.layer3 = self.viewer.add_image(self.init_data_1, {})
        self.layer4 = self.viewer.add_image(self.init_data_1, {})

        self.layers = [self.layer1, self.layer2, self.layer3, self.layer4]

    def compute_vector(self, update: str):
        self.average_change.emit(update)

    def compute_length(self, update: [int, float]):
        self.length_change.emit(update)

    def set_gateway(self, gateway):
        self.gate = gateway
        self.getfile.set_gateway(self.gate)

    def get_gateway(self):
        return self.gate

    @pyqtSlot(object)
    def update_layer_image(self, instance: object):

        if isinstance(instance, PhysicalData):
            print("gui received object of type = "+str(type(instance)))
            self.layer1.vectors = instance.azimuth_vector
            self.layer2.image = instance.scattering
            self.layer3.image = instance.retard
            self.layer4.image = instance.I_trans

            self.layer1.name = "vectors"
            self.layer2.name = 'scattering'
            self.layer3.name = 'retardance'
            self.layer4.name = 'transmission'

            self.update_complete.emit("Received and updated images")
        else:
            print("GUI did not receive Physical Data")
            # self.layer1.vectors = instance
            # self.layer2.image = 65536*np.random.rand(2048,2048)

    def make_connection(self, reconstruction: object):
        from src.DataPipe.PipeFromFiles import PipeFromFiles
        from src.SignalController.SignalController import SignalController
        from src.GUI.qtdesigner.ReconOrderUI import Ui_ReconOrderUI

        if isinstance(reconstruction, PipeFromFiles):
            print("connecting pipe to gui")
            reconstruction.recon_complete.connect(self.update_layer_image)
        elif isinstance(reconstruction, SignalController):
            print("connecting signal controller to gui")
            reconstruction.vector_computed.connect(self.update_layer_image)
        elif isinstance(reconstruction, Ui_ReconOrderUI):
            print("connecting LC calibration to GUI")
            reconstruction.window_update_signal.connect(self.update_layer_image)
        else:
            print("no matching implementation found for: "+str(type(reconstruction)))
