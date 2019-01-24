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

from src.FileManagement.RetrieveData import RetrieveData
from src.DataPipe.PipeToReconOrder import PipeToReconOrder
from src.DataPipe.SignalController import SignalController
from src.Processing.ReconOrder import ReconOrder


class NapariWindowOverlay(QWidget):

    avg_change = pyqtSignal(object)
    update_complete = pyqtSignal(str)

    def __init__(self, window, type='Py4J'):
        super().__init__()

        # Data handling methods
        self.gate = None
        self.getfile = RetrieveData()
        self.type = type
        self.channels = ['Cy5', 'DAPI', 'FITC', 'Rhodamine']
        self.channels_reconOrder = ['State0', 'State1', 'State2', 'State3', 'State4']

        # UI initialization methods
        self.win = window
        self.viewer = self.win.viewer

        # self.meta = dict(name='2D1C', itype='mono')

        #init image data
        self.init_data_1 = 2**16 * np.random.rand(512,512)
        #init vector data
        N = 512
        N2 = N * N
        self.pos = np.zeros((N2, 2), dtype=np.float32)
        dim = np.linspace(0, 4*N - 1, N)
        xv, yv = np.meshgrid(dim, dim)
        self.pos[:, 0] = xv.flatten()
        self.pos[:, 1] = yv.flatten()

        self.layer1 = self.viewer.add_vectors(self.pos)
        # self.layer1.cmap = 'grays'
        self.layer1.bind_to(self.compute_average)

        self.layer2 = self.viewer.add_image(self.init_data_1, {})
        # self.layer2.cmap = 'grays'

        self.layer3 = self.viewer.add_image(self.init_data_1, {})
        # self.layer3.cmap = 'grays'

        self.layer4 = self.viewer.add_image(self.init_data_1, {})
        # self.layer4.cmap = 'grays'

        self.win.show()

        self.layers = [self.layer1, self.layer2, self.layer3, self.layer4]

    def compute_average(self, averaging: str):
        self.avg_change.emit(averaging)

    def set_gateway(self, gateway):
        self.gate = gateway
        self.getfile.set_gateway(self.gate)

    def get_gateway(self):
        return self.gate

    @pyqtSlot(object)
    def update_layer_image(self, instance: object):
        self.win.show()

        if isinstance(instance, ReconOrder):
            print("gui received object of type = "+str(type(instance)))
            self.layer1.vectors = instance.azimuth_vector
            # self.layer2.image = inst_reconOrder.scattering
            self.layer2.image = instance.azimuth_degree
            self.layer3.image = instance.retard
            self.layer4.image = instance.I_trans

            self.update_complete.emit("Received and updated images")

        # elif type(instance) == numpy.ndarray:
        else:
            print("gui received object of type + "+str(type(instance)))
            self.layer1.vectors = instance


    def make_connection(self, reconstruction: object):
        if isinstance(reconstruction, PipeToReconOrder):
            print("connecting pipe to gui")
            reconstruction.recon_complete.connect(self.update_layer_image)
        elif isinstance(reconstruction, SignalController):
            print("connecting signal controller to gui")
            reconstruction.average_computed.connect(self.update_layer_image)
        else:
            print("no matching implementation found for: "+str(type(reconstruction)))
