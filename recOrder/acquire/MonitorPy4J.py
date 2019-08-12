# bchhun, {2019-07-29}

from recOrder.acquire import AcquisitionBase

import numpy as np
import time
from PyQt5.QtCore import QRunnable, QThreadPool


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        super().__init__()
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class MonitorPy4j(AcquisitionBase):

    def __init__(self, gateway_):
        super(MonitorPy4j, self).__init__()
        self.gateway = gateway_
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

    @AcquisitionBase.emitter(channel=4)
    def pull_memmap(self):
        meta = self.ep.getLastMeta()
        while not meta:
            time.sleep(0.00001)
            meta = self.ep.getLastMeta()
        # print('pulling and emitting memmap')
        data = np.memmap(meta.getFilepath(), dtype="uint16", mode='r+', offset=meta.getBufferPosition(),
                         shape=(meta.getxRange(), meta.getyRange()))
        return data

    #to launch monitor upon a signal
    @AcquisitionBase.receiver(channel=0)
    def launch_monitor_in_process(self, *args):
        p = ProcessRunnable(target=self.monitor_process, args=())
        p.start()

    @AcquisitionBase.runnable()
    def monitor_process(self, *args):
        print('monitor launched')
        self.ep.clearQueue()
        count = 0
        while True:
            time.sleep(0.001)

            self.pull_memmap()

            if count >= 1000:
                # timeout is 2.5 minutes = 15000
                print("timeout waiting for more data")
                break
            else:
                count += 1
                if count % 100 == 0:
                    print('waiting')






