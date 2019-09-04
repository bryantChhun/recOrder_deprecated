# bchhun, {2019-07-24}

import numpy as np
import pytest
from PyQt5.QtCore import QObject, pyqtSlot
from numpy.testing import assert_array_equal
from recOrder.analysis._analyze_base import AnalyzeBase

"""

"""


class SampleUserAcquisition(AnalyzeBase):

    def __init__(self):
        super(SampleUserAcquisition, self).__init__()
        self.c = 0

    @AnalyzeBase.emitter
    def update(self):
        print("calling overridden update")
        self.c += 1
        return self.c


class receiver(QObject):

    def __init__(self):
        super(receiver, self).__init__()
        self.ref = 0

    @pyqtSlot(object)
    def rslot(self, value):
        self.ref = 10*value

    def connection(self, signalemitter):
        signalemitter.acquisition_signal.connect(self.rslot)


def test_simple_receiver():
    t = SampleUserAcquisition()
    r = receiver()
    r.connection(t)

    t.update()

    assert(t.c == 1)
    assert(r.ref == 10)