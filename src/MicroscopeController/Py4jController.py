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

from py4j.java_gateway import JavaGateway
import numpy as np
from datetime import datetime
import time

from src.Processing.VectorLayerUtils import compute_average
from src.DataStructures.BackgroundData import BackgroundData
from src.DataStructures.IntensityData import IntensityData
from src.DataStructures.PhysicalData import PhysicalData
from src.Processing.ReconOrder import ReconOrder

from copy import deepcopy

def _snap_channel(channel: str, gateway: JavaGateway):
    """
    Snaps an image on micromanager and returns the memmap data

    :param channel: preset for the configuration group "channel"
    :param gateway: py4j gateway
    :return: np.ndarray-like data
    """
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
    while not gateway.entry_point.fileExists(channel):
        time.sleep(0.0001)
        ct += 1
        if ct >= 10000:
            raise FileExistsError("timeout waiting for file exists")
    stop = datetime.now()
    print("time to check fileExists = %06d" % (stop-start).microseconds)

    data_filename = gateway.entry_point.getFile(channel)

    if data_filename is None:
        print("no file with name %s exists" % channel)

    # retrieve metadata
    meta = gateway.entry_point.getStore(channel)
    data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixeldepth = 8*meta.getBitDepth()
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16
    data = deepcopy(np.memmap(filename=data_filename, dtype=depth, offset=0, shape=data_pixelshape))
    return data


def py4j_collect_background(gateway: JavaGateway, bg_raw: BackgroundData, averaging: int = 5) -> BackgroundData:
    """
    snaps 10 images of each of state0,1,2,3,4.  Averages the 10 for those states

    :param gateway: py4j gateway to micro-manager
    :param bg_raw: BackgroundData object
    :param averaging: number of background frames to snap and average
    :return: BackgroundData object
    """

    # we assume that the image for channel=State0 is the same as that for all other states
    # meta = gateway.entry_point.getStore('State0')
    # data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixelshape = (2048, 2048)

    bg_raw.IExt = np.mean([_snap_channel('State0', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.I90 = np.mean([_snap_channel('State1', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.I135 = np.mean([_snap_channel('State2', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.I45 = np.mean([_snap_channel('State3', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.I0 = np.mean([_snap_channel('State4', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)

    processor = ReconOrder()
    processor.frames = 5
    processor.compute_inst_matrix()
    processor.swing = 0.2
    print("all states snapped")

    #assign intensity states
    # int_obj = IntensityData()
    # int_obj.IExt = bg_raw.IExt
    # int_obj.I0 = bg_raw.I0
    # int_obj.I45 = bg_raw.I45
    # int_obj.I90 = bg_raw.I90
    # int_obj.I135 = bg_raw.I135
    # print("all states assigned to properties")

    # construct and assign stokes to bg_raw
    stk_obj = processor.compute_stokes(bg_raw)
    print("stokes computed")
    bg_raw.s0 = stk_obj.s0
    bg_raw.s1 = stk_obj.s1
    bg_raw.s2 = stk_obj.s2
    bg_raw.s3 = stk_obj.s3
    print('stokes vectors assigned to background object')

    # construct and assign physical to bg_raw
    phys_obj = processor.compute_physical(stk_obj)
    print("physical computed")
    bg_raw.I_trans = phys_obj.I_trans
    bg_raw.retard = phys_obj.retard
    bg_raw.polarization = phys_obj.polarization
    bg_raw.scattering = phys_obj.scattering
    bg_raw.azimuth = phys_obj.azimuth
    print("physical assigned to background object")

    # write to disk
    # create a folder with a name
    # this write should iterate through all BG data stokes? and create a .npy file for each?

    # update UI field to reflect new folder
    # in reconOrderUI we will have the text field trigger another method that
    #   will read the .npy files and update ReconOrderUI's self.Background object

    return bg_raw


def py4j_snap_and_correct(gateway: JavaGateway, background: BackgroundData = None) -> Union[PhysicalData, None]:

    temp_int = IntensityData()
    processor = ReconOrder()
    processor.frames = 5
    processor.swing = 0.1

    try:
        temp_int.IExt = _snap_channel('State0', gateway)
        temp_int.I90 = _snap_channel('State1', gateway)
        temp_int.I135 = _snap_channel('State2', gateway)
        temp_int.I45 = _snap_channel('State3', gateway)
        temp_int.I0 = _snap_channel('State4', gateway)
    except Exception as ex:
        print(str(ex))
        return None

    processor.compute_inst_matrix()
    temp_stokes = processor.compute_stokes(temp_int)
    # averaged_vector = compute_average(temp_stokes,
    #                                   kernel=7,
    #                                   range_x=temp_stokes.s0.shape[0],
    #                                   range_y=temp_stokes.s0.shape[1],
    #                                   func=processor)
    if background:
        temp_physical = processor.correct_background(temp_stokes, background)
    else:
        temp_physical = processor.compute_physical(temp_stokes)
    # scaled_physical = processor.stretch_scale(temp_physical)
    scaled_physical = processor.rescale_bitdepth(temp_physical)
    # scaled_physical.azimuth_vector = averaged_vector

    return scaled_physical

def py4j_calibrate_lc(gateway: JavaGateway):
    #create processing module
    #call CalibrateLC processor

    return None

