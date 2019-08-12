#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :2/20/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6
from typing import Union

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from py4j.java_gateway import JavaGateway
import numpy as np
from datetime import datetime
import time

from recOrder.datastructures.BackgroundData import BackgroundData
from recOrder.datastructures.IntensityData import IntensityData
from recOrder.datastructures.PhysicalData import PhysicalData
# from recOrder.analyze.Processing.ReconOrder import ReconOrder

from copy import deepcopy


def _snap_channel(channel: str, gateway: JavaGateway):
    """
    Snaps an image on micromanager and returns the memmap data

    :param channel: preset for the configuration group "channel"
    :param gateway: py4j gateway
    :return: np.ndarray-like data
    """
    ep = gateway.entry_point
    mmc = gateway.entry_point.getCMMCore()
    mm = gateway.entry_point.getStudio()

    # set channel
    # for some reason, we need a monitor to be sure it gets set....
    mmc.setChannelGroup('Channel')
    start = datetime.now()
    c = 0
    while mmc.getCurrentConfig('Channel') != channel:
        time.sleep(0.0001)
        mmc.setConfig('Channel', channel)
        c += 1
        if c >= 10000:
            raise AttributeError("timeout waiting to set channel")
    stop = datetime.now()
    print("time to check channel = %06d" % (stop-start).microseconds)

    live_manager = mm.getSnapLiveManager()
    live_manager.snap(True)

    # again we need a monitor to be sure file is written
    start = datetime.now()
    ct = 0
    meta = ep.getLastMetaByChannelName(channel)
    # while not gateway.entry_point.fileExists(channel):
    while not meta:
        time.sleep(0.0001)
        ct += 1
        meta = ep.getLastMetaByChannelName(channel)
        if ct >= 10000:
            raise FileExistsError("timeout waiting for file exists")
    stop = datetime.now()
    print("time to check fileExists = %06d" % (stop-start).microseconds)

    # retrieve metadata
    data_filename = meta.getFilepath()
    if data_filename is None:
        print("no file with name %s exists" % channel)
    data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixeldepth = 8*meta.getBitDepth()
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16

    data = deepcopy(np.memmap(filename=data_filename, dtype=depth, offset=0, shape=data_pixelshape))

    if data is None:
        print("data is none")

    return data


# def py4j_collect_background(gateway: JavaGateway, bg_raw: BackgroundData, averaging: int = 5) -> BackgroundData:
#     """
#     snaps 10 images of each of state0,1,2,3,4.  Averages the 10 for those states
#
#     :param gateway: py4j gateway to micro-manager
#     :param bg_raw: BackgroundData object
#     :param averaging: number of background frames to snap and average
#     :return: BackgroundData object
#     """
#
#     # we assume that the image for channel=State0 is the same as that for all other states
#     # meta = gateway.entry_point.getStore('State0')
#     # data_pixelshape = (meta.getxRange(), meta.getyRange())
#     data_pixelshape = (2048, 2048)
#
#     bg_raw.IExt = np.mean([_snap_channel('State0', gateway).flatten() for i in range(0, averaging)], axis=0)\
#         .reshape(data_pixelshape)
#     bg_raw.I90 = np.mean([_snap_channel('State1', gateway).flatten() for i in range(0, averaging)], axis=0)\
#         .reshape(data_pixelshape)
#     bg_raw.I135 = np.mean([_snap_channel('State2', gateway).flatten() for i in range(0, averaging)], axis=0)\
#         .reshape(data_pixelshape)
#     bg_raw.I45 = np.mean([_snap_channel('State3', gateway).flatten() for i in range(0, averaging)], axis=0)\
#         .reshape(data_pixelshape)
#     bg_raw.I0 = np.mean([_snap_channel('State4', gateway).flatten() for i in range(0, averaging)], axis=0)\
#         .reshape(data_pixelshape)
#
#     # processor = ReconOrder()
#     processor.frames = 5
#     processor.compute_inst_matrix()
#     processor.swing = 0.1
#     print("all states snapped")
#
#     #assign intensity states
#     # int_obj = IntensityData()
#     # int_obj.IExt = bg_raw.IExt
#     # int_obj.I0 = bg_raw.I0
#     # int_obj.I45 = bg_raw.I45
#     # int_obj.I90 = bg_raw.I90
#     # int_obj.I135 = bg_raw.I135
#     # print("all states assigned to properties")
#
#     # construct and assign stokes to bg_raw
#     stk_obj = processor.compute_stokes(bg_raw)
#     bg_raw.assign_stokes(stk_obj)
#     # print("stokes computed")
#     # bg_raw.s0 = stk_obj.s0
#     # bg_raw.s1 = stk_obj.s1
#     # bg_raw.s2 = stk_obj.s2
#     # bg_raw.s3 = stk_obj.s3
#     # print('stokes vectors assigned to background object')
#
#     # construct and assign physical to bg_raw
#     phys_obj = processor.compute_physical(stk_obj)
#     bg_raw.assign_physical(phys_obj)
#     # print("physical computed")
#     # bg_raw.I_trans = phys_obj.I_trans
#     # bg_raw.retard = phys_obj.retard
#     # bg_raw.polarization = phys_obj.polarization
#     # bg_raw.scattering = phys_obj.scattering
#     # bg_raw.azimuth = phys_obj.azimuth
#     # print("physical assigned to background object")
#
#     # write to disk
#     # create a folder with a name
#     # this write should iterate through all BG data stokes? and create a .npy file for each?
#
#     # update UI field to reflect new folder
#     # in reconOrderUI we will have the text field trigger another method that
#     #   will read the .npy files and update ReconOrderUI's self.Background object
#
#     return bg_raw


# def py4j_snap_and_correct(gateway: JavaGateway, background: BackgroundData = None) -> Union[PhysicalData, None]:
#
#     temp_int = IntensityData()
#     processor = ReconOrder()
#     processor.frames = 5
#     processor.swing = 0.1
#
#     try:
#         temp_int.IExt = _snap_channel('State0', gateway)
#         temp_int.I90 = _snap_channel('State1', gateway)
#         temp_int.I135 = _snap_channel('State2', gateway)
#         temp_int.I45 = _snap_channel('State3', gateway)
#         temp_int.I0 = _snap_channel('State4', gateway)
#     except Exception as ex:
#         print(str(ex))
#         return None
#
#     processor.compute_inst_matrix()
#     temp_stokes = processor.compute_stokes(temp_int)
#     # averaged_vector = compute_average(temp_stokes,
#     #                                   kernel=7,
#     #                                   range_x=temp_stokes.s0.shape[0],
#     #                                   range_y=temp_stokes.s0.shape[1],
#     #                                   func=processor)
#     if background:
#         temp_physical = processor.correct_background(temp_stokes, background)
#     else:
#         temp_physical = processor.compute_physical(temp_stokes)
#     # scaled_physical = processor.stretch_scale(temp_physical)
#     scaled_physical = processor.rescale_bitdepth(temp_physical)
#     # scaled_physical.azimuth_vector = averaged_vector
#
#     return scaled_physical

def py4j_calibrate_lc(gateway: JavaGateway):
    #create processing module
    #call CalibrateLC processor

    return None


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        QRunnable.__init__(self)
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


# class py4j_monitor_LC(QObject):
#
#     """
#     Method1)
#     - monitor m = ep.getLastMeta()
#     - track: [m1, m2, m3, m4, m5] = same (p, t, z)
#     - on condition : c = State0, State1, State2, State3, State4
#     -   run reconstruction similar to "snap and correct"
#     - repeat
#     Method 2)
#     - use listeners
#     - on listener event, launch same code above
#
#
#     """
#
#     recon_complete = pyqtSignal(object)
#
#     def __init__(self, gateway: JavaGateway, background: BackgroundData):
#         super().__init__()
#
#         self.background = background
#         self.ep = gateway.entry_point
#         self.polstates = set()
#
#         self.temp_int = IntensityData()
#         self.processor = ReconOrder()
#         self.processor.frames = 5
#         self.processor.swing = 0.2
#         print('monitor successfully initialized')
#
#     def monitor(self):
#         print('starting monitor process while loop')
#         count = 0
#         while True:
#             time.sleep(0.001)
#
#             last_meta = self.ep.getLastMeta()
#
#             if last_meta is None:
#                 count += 1
#                 if count % 100 == 0:
#                     print('waiting')
#                 elif count >= 10000:
#                     print("timeout waiting for more data")
#                     break
#                 else:
#                     pass
#             elif last_meta.getChannel() == 0 and (0 not in self.polstates):
#                 self.polstates.add(0)
#                 self.temp_int.IExt = np.memmap(last_meta.getFilepath(),
#                                         dtype="uint16",
#                                         mode='r+',
#                                         offset=0,
#                                         shape=(last_meta.getxRange(), last_meta.getyRange())
#                                         )
#             elif last_meta.getChannel() == 1 and (1 not in self.polstates):
#                 self.polstates.add(1)
#                 self.temp_int.I0 = np.memmap(last_meta.getFilepath(),
#                                         dtype="uint16",
#                                         mode='r+',
#                                         offset=0,
#                                         shape=(last_meta.getxRange(), last_meta.getyRange())
#                                         )
#             elif last_meta.getChannel() == 2 and (2 not in self.polstates):
#                 self.polstates.add(2)
#                 self.temp_int.I45 = np.memmap(last_meta.getFilepath(),
#                                         dtype="uint16",
#                                         mode='r+',
#                                         offset=0,
#                                         shape=(last_meta.getxRange(), last_meta.getyRange())
#                                         )
#             elif last_meta.getChannel() == 3 and (3 not in self.polstates):
#                 self.polstates.add(3)
#                 self.temp_int.I90 = np.memmap(last_meta.getFilepath(),
#                                         dtype="uint16",
#                                         mode='r+',
#                                         offset=0,
#                                         shape=(last_meta.getxRange(), last_meta.getyRange())
#                                         )
#             elif last_meta.getChannel() == 4 and (4 not in self.polstates):
#                 self.polstates.add(4)
#                 self.temp_int.I135 = np.memmap(last_meta.getFilepath(),
#                                         dtype="uint16",
#                                         mode='r+',
#                                         offset=0,
#                                         shape=(last_meta.getxRange(), last_meta.getyRange())
#                                         )
#             elif len(self.polstates) >= 5:
#                 print("\t ===set of five acquired, reconstructing and resetting ====")
#                 self.processor.compute_inst_matrix()
#                 temp_stokes = self.processor.compute_stokes(self.temp_int)
#                 temp_physical = self.processor.correct_background(temp_stokes, self.background)
#                 # scaled_physical = self.processor.stretch_scale(temp_physical)
#                 scaled_physical = self.processor.rescale_bitdepth(temp_physical)
#                 self.polstates = set()
#                 self.recon_complete.emit(scaled_physical)
#             else:
#                 count += 1
#                 if count % 100 == 0:
#                     print('waiting')
#                 elif count >= 10000:
#                     print("timeout waiting for more data")
#                     break
#                 else:
#                     pass
#
#     def launch_monitor(self):
#         print("starting monitor process")
#         self.monitor()
#         # p = ProcessRunnable(target=self.monitor, args=())
#         # p.start()

