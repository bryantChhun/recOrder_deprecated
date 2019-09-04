# bchhun, {2019-08-13}

import pytest
from .. import AcquisitionBase


@pytest.fixture()
def setup_acquisition():
    class EmitterTest(AcquisitionBase):

        @AcquisitionBase.emitter(channel=0)
        def simple_emitter(self):
            return True

    class ReceiverTest(AcquisitionBase):

        @AcquisitionBase.receiver(channel=0)
        def simple_receiver(self, value):
            return value

    return EmitterTest(), ReceiverTest()


def test_emitter(setup_acquisition):

    e, r = setup_acquisition
    e.get_QChannel(0).connect(r.simple_receiver)