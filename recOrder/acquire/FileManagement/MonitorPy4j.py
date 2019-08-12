# bchhun, {2019-07-24}

from recOrder.acquire._acquisition_base import AcquisitionBase

import numpy as np
from PyQt5.QtCore import QThreadPool, QRunnable
import time
from py4j.java_gateway import JavaGateway


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class MonitorPy4j(AcquisitionBase):

    def __init__(self, ):
        super(MonitorPy4j, self).__init__()
        self.gateway = JavaGateway()
        self.ep = self.gateway.entry_point

    def snap_and_retrieve(self):
        """
        use snap/live manager to snap an image then return image
        :return: np.ndarray
        """
        mm = self.ep.getStudio()

        mm.live().snap(True)

        meta = self.ep.getLastMeta()
        # meta is not immediately available -> exposure time + lc delay
        while meta is None:
            meta = self.ep.getLastMeta()

        data = np.memmap(meta.getFilepath(), dtype="uint16", mode='r+', offset=0,
                         shape=(meta.getxRange(), meta.getyRange()))
        return data

    def _start_monitor(self):
        self.ep.clearQueue()

        count = 0
        while True:
            time.sleep(0.001)

            meta = self.ep.getLastMeta()
            if meta is not None:
                data = np.memmap(meta.getFilepath(), dtype="uint16", mode='r+', offset=0,
                                 shape=(meta.getxRange(), meta.getyRange()))
                self.acquisition_signal.emit(data)

            if count >= 1000:
                # timeout is 2.5 minutes = 15000
                print("timeout waiting for more data")
                break
            else:
                count += 1
                if count % 100 == 0:
                    print('waiting')





