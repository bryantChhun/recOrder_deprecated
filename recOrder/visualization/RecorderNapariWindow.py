# bchhun, {2019-07-24}

from recOrder.visualization._visualize_base import VisualizeBase
from recOrder.datastructures.PhysicalData import PhysicalData
from recOrder.datastructures.BackgroundData import BackgroundData
import numpy as np
import napari
from typing import Union

"""
A multi-layer napari window to display each of reconstructed birefringence images:
- polarization
- retardance
- transmission
- orientation (vector layer)

"""


class RecorderNapariWindow(VisualizeBase):

    def __init__(self):
        super().__init__()
        print('setting up napari window')
        self.viewer = napari.Viewer()

        N = 2048

        # init image data
        # self.init_data_0 = 2 ** 16 * np.random.rand(1, N, N)
        self.init_data_1 = 2 ** 16 * np.random.rand(1, N, N)
        self.init_data_2 = 2 ** 16 * np.random.rand(1, N, N)
        self.init_data_3 = 2 ** 16 * np.random.rand(1, N, N)

        # init layers with vector data and subscribe to gui notifications
        # self.layer0 = self.viewer.add_image(self.init_data_0)
        self.layer0 = None
        self.layer1 = self.viewer.add_image(self.init_data_1)
        self.layer2 = self.viewer.add_image(self.init_data_2)
        self.layer3 = self.viewer.add_image(self.init_data_3)

        # self.layer4 = self.viewer.add_vectors(self.pos)

    @VisualizeBase.receiver(channel=1)
    def update_layer_image(self, instance: Union[PhysicalData, BackgroundData, np.array, tuple]):
        print('gui is notified of new data')

        if isinstance(instance, PhysicalData) and not isinstance(instance, BackgroundData):
            print('gui received PhysicalData')
            # self.layer1._node.set_data(instance.polarization)
            # self.layer1._node.update()
            # self.layer2._node.set_data(instance.retard)
            # self.layer2._node.update()
            # self.layer3._node.set_data(instance.I_trans)
            # self.layer3._node.update()

            # self.layer4.vectors = np.swapaxes(instance.azimuth_vector, 0, 1)
            # self.layer4._raw_dat = instance.azimuth_vector

            pol = instance.polarization
            ret = instance.retard
            trans = instance.I_trans

            self.layer1.data = np.append(self.layer1.data, np.reshape(pol, (1, pol.shape[0], pol.shape[1])), axis=0)
            self.layer2.data = np.append(self.layer2.data, np.reshape(ret, (1, ret.shape[0], ret.shape[1])), axis=0)
            self.layer3.data = np.append(self.layer3.data, np.reshape(trans, (1, trans.shape[0], trans.shape[1])), axis=0)

            # self.layer1.name = "vectors"
            # self.layer0.name = 'orientation'
            self.layer1.name = 'polarization'
            self.layer2.name = 'retardance'
            self.layer3.name = 'transmission'

            self.display_ready(True)

        # replace snap image layer with new data.
        elif type(instance) == np.ndarray or type(instance) == np.memmap:
            print("gui received direct array")
            if self.viewer.layers[-1].name != 'snap':
                self.viewer.add_image(instance)
                self.viewer.layers[-1].name = "snap"
            else:
                self.viewer.layers[-1].data = instance

        elif type(instance) == tuple:
            print("gui received orientation data")
            orientation = instance[0]
            if not self.layer0:
                self.layer0 = self.viewer.add_image(orientation.reshape(1,
                                                                        orientation.shape[0],
                                                                        orientation.shape[1], 3))
            else:
                self.layer0.data = np.append(self.layer0.data,
                                             np.reshape(orientation,
                                                        (1, orientation.shape[0], orientation.shape[1],3)
                                                        ),
                                             axis=0)
            self.layer0.name = 'orientation'

        else:
            print("gui didn't receive any recognized data type %s"+str(type(instance)))

    @VisualizeBase.emitter(channel=9)
    def display_ready(self, value):
        return value
