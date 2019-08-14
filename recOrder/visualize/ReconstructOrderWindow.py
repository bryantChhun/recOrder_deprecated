# bchhun, {2019-07-24}

from recOrder.visualize._visualize_base import VisualizeBase
from recOrder.datastructures.PhysicalData import PhysicalData
from recOrder.datastructures.BackgroundData import BackgroundData
import numpy as np
import napari


class ReconstructOrderWindow(VisualizeBase):

    def __init__(self):
        super().__init__()
        print('setting up napari window')
        self.viewer = napari.Viewer()

        N = 2048

        # init image data
        self.init_data_1 = 2 ** 16 * np.random.rand(N, N)

        # init layers with vector data and subscribe to gui notifications
        self.layer1 = self.viewer.add_image(self.init_data_1)
        self.layer2 = self.viewer.add_image(self.init_data_1)
        self.layer3 = self.viewer.add_image(self.init_data_1)

        # self.layer1 = self.viewer.add_vectors(self.pos)

    @VisualizeBase.receiver(channel=4)
    def update_layer_image(self, instance: object):
        print('gui is notified of new data')

        if isinstance(instance, PhysicalData) and not isinstance(instance, BackgroundData):
            print('gui received PhysicalData')
            # self.layer1.vectors = np.swapaxes(instance.azimuth_vector, 0, 1)
            # self.layer1._raw_dat = instance.azimuth_vector
            self.layer1._node.set_data(instance.depolarization)
            self.layer1._node.update()
            self.layer2._node.set_data(instance.retard)
            self.layer2._node.update()
            self.layer3._node.set_data(instance.I_trans)
            self.layer3._node.update()

            # self.layer1.name = "vectors"
            self.layer1.name = 'depolarization'
            self.layer2.name = 'retardance'
            self.layer3.name = 'transmission'

        # replace snap image layer with new data.
        elif type(instance) == np.ndarray or type(instance) == np.memmap:
            print("gui received direct array")
            if self.viewer.layers[-1].name != 'snap':
                self.viewer.add_image(instance)
                self.viewer.layers[-1].name = "snap"
            else:
                self.viewer.layers[-1].data = instance

            # self.viewer.layers.remove(2)
            # self.viewer.layers.remove(3)
            # self.viewer.layers.remove(4)

        else:
            print("gui didn't receive any data")