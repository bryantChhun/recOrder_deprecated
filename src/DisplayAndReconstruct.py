#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/3/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import sys
from PyQt5.QtWidgets import QApplication

from py4j.java_gateway import JavaGateway

from src.GUI import NapariWindow
from src.DataPipe import BasicMonitorDatastores

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