#!/usr/bin/env python
# title           : DisplayAndReconstruct.py
# description     :Simple execution of Reconstruction Package
# author          :bryant.chhun
# date            :12/3/18
# version         :0.0
# usage           :from terminal: python DisplayAndReconstruct.py
# notes           :
# python_version  :3.6

"""
This code describes simple execution of Reconstruction and Visualization code.
    Data is received from Micromanager using mm2Python, is processed in this python package,
    and then is displayed in a viewer.
"""

import sys
from PyQt5.QtWidgets import QApplication

from py4j.java_gateway import JavaGateway

from src.GUI import NapariWindow
from src.FileManagement import BasicMonitorDatastores

if __name__ == '__main__':
    # starting
    application = QApplication(sys.argv)

    gateway = JavaGateway()

    win = NapariWindow.NapariWindow(gateway)
    monitor = BasicMonitorDatastores.MonitorDatastores(gateway)

    win.make_conection(monitor)
    monitor.make_connection(win)

    monitor.run()

    sys.exit(application.exec_())