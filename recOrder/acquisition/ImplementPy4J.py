# bchhun, {2019-07-24}

from ..acquisition import AcquisitionBase

import numpy as np
from py4j.java_gateway import JavaGateway, CallbackServerParameters, GatewayParameters


class ImplementPy4J(AcquisitionBase):

    def __init__(self):
        super(ImplementPy4J, self).__init__()
        self.gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_field=True),
                                   callback_server_parameters=CallbackServerParameters())
        self.ep = self.gateway.entry_point
        listener = self.ep.getListener()
        listener.registerListener(self)

    @AcquisitionBase.emitter(channel=4)
    def notify(self, obj):
        """
        When notified by java, this event is called
        """
        print("notified by java via java interface")
        meta = self.ep.getLastMeta()
        while meta is None:
            meta = self.ep.getLastMeta()

        data = np.memmap(meta.getFilepath(), dtype="uint16", mode='r+', offset=0,
                         shape=(meta.getxRange(), meta.getyRange()))
        return data
