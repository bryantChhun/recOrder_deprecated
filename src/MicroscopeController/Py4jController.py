#!/usr/bin/env python
# title           :
# description     :
# author          :bryant.chhun
# date            :2/20/19
# version         :0.0
# usage           :
# notes           :
# python_version  :3.6

from py4j.java_gateway import JavaGateway
import numpy as np
import time

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
    c=0
    while mmc.getCurrentConfig('Channel') != channel:
        time.sleep(0.001)
        mmc.setConfig('Channel', channel)
        c += 1
        if c >= 1000:
            print('timeout waiting to set channel')
            print('current config is = '+mmc.getCurrentConfig('Channel'))
            break
    print("time to check channel = %04d" % c)

    live_manager = mm.getSnapLiveManager()
    live_manager.snap(True)

    # again we need a monitor to be sure file is written
    ct = 0
    while not gateway.entry_point.fileExists(channel):
        time.sleep(0.001)
        ct += 1
        if ct >= 1000:
            print('timeout waiting for file exists')
            break
    print("time to check fileExists = %04d" % ct)

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


def py4j_collect_background(gateway: JavaGateway, bg_raw: BackgroundData, averaging: int = 10) -> BackgroundData:
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

    bg_raw.state0 = np.mean([_snap_channel('State0', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.state1 = np.mean([_snap_channel('State1', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.state2 = np.mean([_snap_channel('State2', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.state3 = np.mean([_snap_channel('State3', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    bg_raw.state4 = np.mean([_snap_channel('State4', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape)
    processor = ReconOrder()
    processor.frames = 5
    print("all states snapped")

    #assign intensity states
    processor.state = (0, bg_raw.state0)
    processor.state = (1, bg_raw.state1)
    processor.state = (2, bg_raw.state2)
    processor.state = (3, bg_raw.state3)
    processor.state = (4, bg_raw.state4)
    print("all states assigned to properties")

    # construct and assign stokes to bg_raw
    processor.compute_stokes()
    print("stokes computed")
    bg_raw.s0 = processor.s0
    bg_raw.s1 = processor.s1
    bg_raw.s2 = processor.s2
    bg_raw.s3 = processor.s3
    print('stokes vectors assigned to background object')

    # construct and assign physical to bg_raw
    processor.compute_physical()
    print("physical computed")
    bg_raw.I_trans = processor.I_trans
    bg_raw.retard = processor.retard
    bg_raw.polarization = processor.polarization
    bg_raw.scattering = processor.scattering
    bg_raw.azimuth = processor.azimuth
    print("physical assigned to background object")

    # write to disk
    # create a folder with a name
    # this write should iterate through all BG data stokes? and create a .npy file for each?

    # update UI field to reflect new folder
    # in reconOrderUI we will have the text field trigger another method that
    #   will read the .npy files and update ReconOrderUI's self.Background object

    return bg_raw


def py4j_snap_and_correct(gateway: JavaGateway, background: BackgroundData) -> PhysicalData:

    temp_int = IntensityData()
    processor = ReconOrder()
    processor.frames = 5

    temp_int.IExt = _snap_channel('State0', gateway)
    temp_int.I0 = _snap_channel('State1', gateway)
    temp_int.I45 = _snap_channel('State2', gateway)
    temp_int.I90 = _snap_channel('State3', gateway)
    temp_int.I135 = _snap_channel('State4', gateway)

    temp_stokes = processor.compute_stokes(temp_int)
    temp_physical = processor.correct_background(temp_stokes, background)

    return temp_physical

def py4j_calibrate_lc(gateway: JavaGateway):
    #create processing module
    #call CalibrateLC processor

    return None

