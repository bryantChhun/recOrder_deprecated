# #!/usr/bin/env python
# # title           : this_python_file.py
# # description     :This will create a header for a python script.
# # author          :bryant.chhun
# # date            :12/6/18
# # version         :0.0
# # usage           :python this_python_file.py -flags
# # notes           :
# # python_version  :3.6
#
#
# from PyQt5.QtWidgets import QWidget
# from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool
# import numpy as np
#
# from recOrder.datastructures import BackgroundData
# from recOrder.acquire.FileManagement.RetrieveFiles import RetrieveData
# from recOrder.datastructures.PhysicalData import PhysicalData
#
#
# class ProcessRunnable(QRunnable):
#     def __init__(self, target, args):
#         QRunnable.__init__(self)
#         self.t = target
#         self.args = args
#
#     def run(self):
#         self.t(*self.args)
#
#     def start(self):
#         QThreadPool.globalInstance().start(self)
#
#
# class NapariWindow(QWidget):
#
#     average_change = pyqtSignal(list)
#     # length_change = pyqtSignal(float)
#
#     def __init__(self, viewer, type='Py4J'):
#         super().__init__()
#
#         # Data handling methods
#         self.gate = None
#         self.getfile = RetrieveData()
#         self.type = type
#         self.channels = ['Cy5', 'DAPI', 'FITC', 'Rhodamine']
#         self.channels_reconOrder = ['State0', 'State1', 'State2', 'State3', 'State4']
#
#         # UI initialization methods
#         self.viewer = viewer
#
#         #init vector data
#         N = 2048
#         self.pos = np.zeros((N, N, 2), dtype=np.float32)
#         dim = np.linspace(0, N - 1, N)
#         xv, yv = np.meshgrid(dim, dim)
#         self.pos[:, :, 0] = xv
#         self.pos[:, :, 1] = yv
#
#         #init image data
#         self.init_data_1 = 2**16 * np.random.rand(N,N)
#
#         #init layers with vector data and subscribe to gui notifications
#         self.layer2 = self.viewer.add_image(self.init_data_1)
#         self.layer3 = self.viewer.add_image(self.init_data_1)
#         self.layer4 = self.viewer.add_image(self.init_data_1)
#
#         self.layer1 = self.viewer.add_vectors(self.pos)
#         # self.layer1._default_avg = self.run_faster
#
#     # custom averaging is no longer supported in napari
#     # def run_faster(self):
#     #     process = ProcessRunnable(target=self.update_average, args=())
#     #     process.start()
#     #
#     # def update_average(self):
#     #     """
#     #     called by the UI
#     #     emits a signal received by PipeFromFiles, which initiates calculation
#     #     PipeFromFiles emits signal to this class's "update_layer_image"
#     #     :return:
#     #     """
#     #     if self.layer1._averaging == 1:
#     #         return self.layer1._current_data
#     #     else:
#     #         self.average_change.emit([self.layer1._averaging,
#     #                                   self.layer1._original_data.shape[0],
#     #                                   self.layer1._original_data.shape[1]])
#
#     def set_gateway(self, gateway):
#         self.gate = gateway
#         self.getfile.set_gateway(self.gate)
#
#     def get_gateway(self):
#         return self.gate
#
#     @pyqtSlot(object)
#     def update_layer_image(self, instance: object):
#         print('gui is notified of new data')
#
#         if isinstance(instance, PhysicalData) and not isinstance(instance, BackgroundData):
#             print('gui received PhysicalData')
#             self.layer1.vectors = np.swapaxes(instance.azimuth_vector, 0, 1)
#             self.layer1._raw_dat = instance.azimuth_vector
#             self.layer2.image = instance.scattering
#             self.layer3.image = instance.retard
#             self.layer4.image = instance.I_trans
#
#             self.layer1.name = "vectors"
#             self.layer2.name = 'scattering'
#             self.layer3.name = 'retardance'
#             self.layer4.name = 'transmission'
#
#         else:
#             print("GUI did not receive Physical Data")