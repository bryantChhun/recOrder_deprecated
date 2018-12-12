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
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import threading

class MonitorDatastores(QObject):

    newImage = pyqtSignal(int)

    '''
    flow controls:
        self.switch answers "Is data rendered to UI? ok to query next image?"
        self.quad answers "have we already rendered this image in this set of four channels?"
    '''
    def __init__(self, gate):
        super().__init__()
        self.gateway = gate
        self.switch = True
        self.quad = set()

    @pyqtSlot()
    def toggle_switch(self):
        self.switch = not self.switch

    def make_connection(self, notify_object):
        notify_object.successful_update.connect(self.toggle_switch)

    def start_monitor(self):

        count = 0
        while True:
            time.sleep(0.001)

            # use lambdas here?
            if not self.switch:
                continue
            elif self.gateway.storeByChannelNameExists("Cy5") and (0 not in self.quad):
                self.newImage.emit(0)
                print("Cy5 image emitting")
                self.quad.add(0)
                self.switch = False
            elif self.gateway.storeByChannelNameExists("DAPI") and (1 not in self.quad):
                self.newImage.emit(1)
                print("DAPI image emitting")
                self.quad.add(1)
                self.switch = False
            elif self.gateway.storeByChannelNameExists("FITC") and (2 not in self.quad):
                self.newImage.emit(2)
                print("FITC image emitting")
                self.quad.add(2)
                self.switch = False
            elif self.gateway.storeByChannelNameExists("Rhodamine") and (3 not in self.quad):
                self.newImage.emit(3)
                print("Rhodamine image emitting")
                self.quad.add(3)
                self.switch = False
            elif count >= 10000:
                print("timeout waiting for more data")
                break
            elif len(self.quad) >= 4:
                print("\t ===set of four acquired, resetting===")
                self.quad = set()
                #self.quad.clear()
            else:
                count += 1
                if count%100 == 0:
                    print('waiting')

    def run(self):
        t1 = threading.Thread(target=self.start_monitor)
        t1.start()