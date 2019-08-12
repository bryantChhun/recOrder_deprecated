# bchhun, {2019-07-31}

from ..acquire._acquisition_base import AcquisitionBase
from ..datastructures.IntensityData import IntensityData
from ..microscope.mm2python_simple import get_image_by_channel_name
import time


class ReconstructOrderMonitor(AcquisitionBase):

    def __init__(self, mm_channel_names: list, int_channel_names: list, gateway, emitter_channel=0):
        super(AcquisitionBase, self).__init__()
        self.channel = emitter_channel
        self.mm_channel_names = mm_channel_names

        self.gateway = gateway
        self.ep = self.gateway.entry_point
        self.mm = self.ep.getStudio()
        self.ep.clearQueue()

        self.int_dat = IntensityData()
        self.int_dat.channel_names = int_channel_names

        self.pol_states = set()

        self.send_completed_int_data = AcquisitionBase.emitter(channel=self.channel)(self.send_completed_int_data)

    def start_monitor(self, timeout=2.5):

        count = 0
        while True:
            time.sleep(0.001)

            if not self.gateway:
                break
            elif self._gateway.storeByChannelNameExists(self.mm_channel_names[0]) and (0 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[0], self.ep))
                self.pol_states.add(0)
                count += 1

            elif self._gateway.storeByChannelNameExists(self.mm_channel_names[1]) and (1 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[1], self.ep))
                self.pol_states.add(1)
                count += 1

            elif self._gateway.storeByChannelNameExists(self.mm_channel_names[2]) and (2 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[2], self.ep))
                self.pol_states.add(2)
                count += 1

            elif self._gateway.storeByChannelNameExists(self.mm_channel_names[3]) and (3 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[3], self.ep))
                self.pol_states.add(3)
                count += 1

            elif self._gateway.storeByChannelNameExists(self.mm_channel_names[4]) and (4 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[4], self.ep))
                self.pol_states.add(4)
                count += 1

            elif count >= (timeout*60)/0.001:
                #timeout is 2.5 minutes = 15000
                print("timeout waiting for more data")
                break
            elif len(self.pol_states) >= 5:
                print("\t ===set of five acquired, emitting and resetting ===")
                self.send_completed_int_data()

                self.int_dat = IntensityData()
                self.pol_states = set()
            else:
                count += 1
                if count%100 == 0:
                    print('waiting')

    #this is annotated to emit an intensity data object
    def send_completed_int_data(self):
        return self.int_dat
