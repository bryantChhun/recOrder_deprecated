#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/6/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

from abc import ABCMeta, abstractmethod

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import numpy as np

class WindowInterface:
    __metaclass__ = ABCMeta

    # @property
    # def gui_updated(self): return successful_update = pyqtSignal()

    @abstractmethod
    @pyqtSlot(int)
    def update_layer_image(self, layer_index: int): raise NotImplementedError

    @abstractmethod
    def make_connection(self, notify_object): raise NotImplementedError

    @classmethod
    def version(self): return "1.0"