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

    mmc.setChannelGroup('Channel')
    mmc.setConfig('Channel', channel)
    livemanager = mm.getSnapLiveManager()
    livemanager.snap(True)

    ct = 0
    while not gateway.entry_point.fileExists(channel):
        time.sleep(0.01)
        ct += 1
        if ct >= 1000:
            print('timeout waiting for file exists')
            break

    data_filename = gateway.entry_point.getFile(channel)
    if data_filename is None:
        print("no file with name %s exists" % channel)
    store = gateway.entry_point.getStore(channel)
    data_pixelshape = (store.x_dim, store.y_dim)
    data_pixeldepth = 8*store.bitdepth
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16
    data = deepcopy(np.memmap(filename=data_filename, dtype=depth, offset=0, shape=data_pixelshape))
    return data


def py4j_snap_and_correct(gateway: JavaGateway, background: BackgroundData):
    try:
        temp_int = IntensityData()
        temp_physical = PhysicalData()
        processor = ReconOrder()
        processor.frames = 5

        temp_int.Iext = _snap_channel('State0', gateway)
        temp_int.I0 = _snap_channel('State1', gateway)
        temp_int.I45 = _snap_channel('State2', gateway)
        temp_int.I90 = _snap_channel('State3', gateway)
        temp_int.I135 = _snap_channel('State4', gateway)

        processor.IntensityData = temp_int
    except Exception as ex:
        print("Exception when collecting background: " + str(ex))
        return False

    try:
        processor.compute_stokes()
        processor.compute_physical()
        processor.correct_background(background)
        temp_physical.I_trans = processor.I_trans
        temp_physical.retard = processor.retard
        temp_physical.polarization = processor.polarization
        temp_physical.scattering = processor.scattering
        temp_physical.azimuth = processor.azimuth

        return temp_physical
    except Exception as ex:
        print("Exception when processing background: " +str(ex))
        return False


def py4j_collect_background(gateway: JavaGateway, bg_raw: BackgroundData):
    # add query of State0,1,2,3,4 in config group channel
    # should be accomplished through micromanager
    try:
        bg_raw.state0 = _snap_channel('State0', gateway)
        bg_raw.state1 = _snap_channel('State1', gateway)
        bg_raw.state2 = _snap_channel('State2', gateway)
        bg_raw.state3 = _snap_channel('State3', gateway)
        bg_raw.state4 = _snap_channel('State4', gateway)
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

        return bg_raw

        # write to disk
            # create a folder with a name
            # this write should iterate through all attributes and create a .npy file for each?

        # update UI field to reflect new folder
        # in reconOrderUI we will have the text field trigger another method that
        #   will read the .npy files and update ReconOrderUI's self.Background object

    except Exception as ex:
        print("Exception when collecting background: "+str(ex))
        return False


def py4j_calibrate_lc(gateway: JavaGateway):
    #create processing module
    #call CalibrateLC processor


    return None

