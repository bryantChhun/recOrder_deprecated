# bchhun, {2019-07-31}

from ..acquisition._acquisition_base import AcquisitionBase
from ..datastructures.IntensityData import IntensityData
from ..microscope.mm2python_simple import get_image_by_channel_name
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

"""
monitor to retrieve data from micro-manager when a set of 5 polstates are available
automatically launches reconstruction and displays this
will not fetch new data until the GUI is fully updated
"""
class ReconOrderMonitor(AcquisitionBase):

    def __init__(self, mm_channel_names: list, int_channel_names: list, gateway):
        super(AcquisitionBase, self).__init__()
        self.mm_channel_names = mm_channel_names

        self.gateway = gateway
        self.ep = self.gateway.entry_point
        self.mm = self.ep.getStudio()
        self.ep.clearQueue()

        self.int_dat = IntensityData()
        self.int_dat.channel_names = int_channel_names

        self.pol_states = set()
        self.display_ready = True
        self.monitor_flag = False

    @AcquisitionBase.receiver(channel=11)
    def display_response(self, value):
        self.display_ready = value

    @AcquisitionBase.receiver(channel=19)
    def stop_monitor(self):
        self.monitor_flag = True

    @AcquisitionBase.receiver(channel=10)
    def start_monitor(self):
        p = ProcessRunnable(target=self._start_monitor_runnable, args=())
        p.start()

    def _start_monitor_runnable(self, timeout=2.5):

        self.int_dat = IntensityData()
        self.pol_states = set()
        self.display_ready = True

        count = 0
        while True:
            time.sleep(0.001)

            if not self.gateway:
                print("no gateway defined")
                break
            elif self.monitor_flag:
                print("stopping data monitor")
                self.monitor_flag = False
                break

            elif not self.display_ready:
                self.pol_states = set()
                self.int_dat = IntensityData()
                count += 1
                continue

            elif self.ep.storeByChannelNameExists(self.mm_channel_names[0]) and (0 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[0], self.ep))
                self.pol_states.add(0)
                count += 1

            elif self.ep.storeByChannelNameExists(self.mm_channel_names[1]) and (1 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[1], self.ep))
                self.pol_states.add(1)
                count += 1

            elif self.ep.storeByChannelNameExists(self.mm_channel_names[2]) and (2 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[2], self.ep))
                self.pol_states.add(2)
                count += 1

            elif self.ep.storeByChannelNameExists(self.mm_channel_names[3]) and (3 not in self.pol_states):
                self.int_dat.add_image(get_image_by_channel_name(self.mm_channel_names[3], self.ep))
                self.pol_states.add(3)
                count += 1

            elif self.ep.storeByChannelNameExists(self.mm_channel_names[4]) and (4 not in self.pol_states):
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
                self.display_ready = False
            else:
                count += 1
                if count%100 == 0:
                    print('waiting')

    @AcquisitionBase.emitter(channel=11)
    def send_completed_int_data(self):
        return self.int_dat
