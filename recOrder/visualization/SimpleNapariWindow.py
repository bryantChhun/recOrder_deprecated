# bchhun, {2019-07-29}

from ..visualization import VisualizeBase
import numpy as np
import napari

"""
A simple napari window that displays a single image layer
"""

class SimpleNapariWindow(VisualizeBase):

    def __init__(self, window_channel=0):
        super().__init__()
        print('setting up napari window')
        self.viewer = napari.Viewer()

        N = 2048

        # init image data
        self.init_data_1 = 2 ** 16 * np.random.rand(N, N)

        # init layers with vector data and subscribe to gui notifications
        self.layer1 = self.viewer.add_image(self.init_data_1)

        # Instance decoration of update_layer_image
        self.update_layer_image = VisualizeBase.receiver(channel=window_channel)(self.update_layer_image)

    # class decoration.  Instance channel overrides this one
    @VisualizeBase.receiver(channel=4)
    def update_layer_image(self, data: object):
        # print('gui is notified of new data')
        try:
            self.layer1._node.set_data(data)
            self.layer1._node.update()
            # self.layer1.data = data
            self.layer1.name = "snap"
        except Exception as ex:
            print("exception while updating gui "+str(ex))
