#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/3/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import time
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThreadPool, QRunnable


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class MonitorDatastores(QObject):

    newImage = pyqtSignal(tuple)

    '''
    flow controls:
        self.ui_ready answers "Is data rendered to UI? ok to query next image?"
        self.polstates answers "have we already rendered this image in this set of four channels?"
    '''
    def __init__(self, gate):
        super().__init__()
        self._gateway = gate
        self.ui_ready = True
        self.polstates = set()

    @property
    def gateway(self):
        return self._gateway

    @gateway.setter
    def gateway(self, gateway):
        self._gateway = gateway

    @pyqtSlot(bool)
    def _toggle_switch(self, ready: bool):
        self.ui_ready = ready

    def make_connection(self, notify_object):
        # if isinstance(notify_object, PipeFromPy4j):
        notify_object.poll_newdata.connect(self._toggle_switch)
        # else:
        #     notify_object.successful_update.connect(self._toggle_switch)

    def _start_monitor(self):

        count = 0
        while True:
            time.sleep(0.001)

            if not self.ui_ready:
                continue
            elif not self._gateway:
                continue
            elif self._gateway.storeByChannelNameExists("State0") and (0 not in self.polstates):
                self.newImage.emit((0, self._gateway.retrieveFileByChannelName("State0")))
                print("Pol State 0 image emitting")
                self.polstates.add(0)
                self.ui_ready = False
            elif self._gateway.storeByChannelNameExists("State1") and (1 not in self.polstates):
                self.newImage.emit((1, self._gateway.retrieveFileByChannelName("State1")))
                print("Pol State 1 image emitting")
                self.polstates.add(1)
                self.ui_ready = False
            elif self._gateway.storeByChannelNameExists("State2") and (2 not in self.polstates):
                self.newImage.emit((2, self._gateway.retrieveFileByChannelName("State2")))
                print("Pol State 2 image emitting")
                self.polstates.add(2)
                self.ui_ready = False
            elif self._gateway.storeByChannelNameExists("State3") and (3 not in self.polstates):
                self.newImage.emit((3, self._gateway.retrieveFileByChannelName("State3")))
                print("Pol State 3 image emitting")
                self.polstates.add(3)
                self.ui_ready = False
            elif self._gateway.storeByChannelNameExists("State4") and (4 not in self.polstates):
                self.newImage.emit((4, self._gateway.retrieveFileByChannelName("State4")))
                print("Pol State 4 image emitting")
                self.polstates.add(4)
                self.ui_ready = False
            elif count >= 1000:
                #timeout is 2.5 minutes = 15000
                print("timeout waiting for more data")
                break
            elif len(self.polstates) >= 5:
                print("\t ===set of five acquired, resetting===")
                self.polstates = set()
            else:
                count += 1
                if count%100 == 0:
                    print('waiting')

    def run(self):
        self._t1 = ProcessRunnable(target=self._start_monitor, args=())
        self._t1.start()

