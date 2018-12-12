#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/3/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import numpy as np

from src.FileManagement.RetrieveData import RetrieveFile

from napari_gui.elements import Window

#ToDO: turn this into an ABC and create dependencies for each mode we care to use
class NapariWindow(QWidget):

    successful_update = pyqtSignal()

    def __init__(self, gate, type='Py4J'):
        super().__init__()

        # Data handling methods
        self.gateway = gate
        self.getfile = RetrieveFile(self.gateway)
        self.type = type
        self.channels = ['Cy5', 'DAPI', 'FITC', 'Rhodamine']
        self.channels_reconOrder = ['State0', 'State1', 'State2', 'State3', 'State4']

        # UI initialization methods
        self.win = Window()
        self.viewer = self.win.add_viewer()

        self.meta = dict(name='3D1C', itype='mono')
        h, w, d = 512, 512, 1
        self.init_data_1 = (65536 * 1 / 4) * np.zeros(shape=(h, w), dtype='uint16')
        self.init_data_2 = (65536 * 2 / 4) * np.zeros(shape=(h, w), dtype='uint16')
        self.init_data_3 = (65536 * 3 / 4) * np.zeros(shape=(h, w), dtype='uint16')
        self.init_data_4 = (65536 * 4 / 4) * np.zeros(shape=(h, w), dtype='uint16')

        self.layer1 = self.viewer.add_image(self.init_data_1, self.meta)
        self.layer1.cmap = 'grays'
        self.layer1.interpolation = 'spline36'
        self.layer1.clim = np.min(self.init_data_1), np.max(self.init_data_1)

        self.layer2 = self.viewer.add_image(self.init_data_2, self.meta)
        self.layer2.cmap = 'blues'
        self.layer2.interpolation = 'spline36'
        self.layer2.translate = [self.init_data_1.shape[1] + 10]
        self.layer2.clim = np.min(self.init_data_2), np.max(self.init_data_2)

        self.layer3 = self.viewer.add_image(self.init_data_3, self.meta)
        self.layer3.cmap = 'greens'
        self.layer3.interpolation = 'spline36'
        self.layer3.translate = [0, self.init_data_1.shape[1] + 10]
        self.layer3.clim = np.min(self.init_data_3), np.max(self.init_data_3)

        self.layer4 = self.viewer.add_image(self.init_data_4, self.meta)
        self.layer4.cmap = 'orange'
        self.layer4.interpolation = 'spline36'
        self.layer4.translate = [self.init_data_1.shape[1] + 10, self.init_data_1.shape[1] + 10]
        self.layer4.clim = np.min(self.init_data_4), np.max(self.init_data_4)

        self.viewer.camera.set_range((0, w * 2), (0, h * 2))

        self.win.show()

        self.layers = [self.layer1, self.layer2, self.layer3, self.layer4]


    # def grab_filename(self, channel_name):
    #     return self.getfile.get_file_name(channel_name, type=self.type)
    #
    # def grab_frame(self, channel_name):
    #     try:
    #         filename = self.grab_filename(channel_name)
    #         return np.memmap(filename, dtype='uint16', offset=0, mode='r', shape=(512, 512, 1))
    #     except ValueError:
    #         raise ValueError

    def get_window(self):
        return self.win

    def get_layers(self):
        return [self.layer1, self.layer2, self.layer3, self.layer4]

    @pyqtSlot(int)
    def update_layer_image(self, layer_index: int):
        self.win.show()
        try:
            if self.type == "Test":
                new_image = self.getfile.get_array_from_filename(self.channels_reconOrder[layer_index], type='Test')
            else:
                new_image = self.getfile.get_array_from_filename(self.channels[layer_index], type='Py4J')

            if len(self.layers[layer_index].image.shape) == 2:
                print("\t replacing init image")
                self.layers[layer_index].image = new_image
            else:
                # Append to end of stack
                # self.layers[layer_index].image = np.append(self.layers[layer_index].image, new_image, axis=2)

                # Append to front of stack
                # self.layers[layer_index].image = np.concatenate( (new_image, self.layers[layer_index].image), axis=2)

                # Replace image
                # self.layers[layer_index].image = new_image

                # Process and replace image
                # new_image = cv2_sobel_edge_with_binary(new_image)
                self.layers[layer_index].image = new_image

            print("\t window signaled, updating image")
            print("\t image #, z-index: (int, total-z) = (%01d, %02d)" % (layer_index, self.layers[layer_index].image.shape[0]))
            self.layers[layer_index].clim = np.min(new_image), np.max(new_image)
            self.successful_update.emit()
        except ValueError:
            pass

    def make_conection(self, notify_object):
        notify_object.newImage.connect(self.update_layer_image)