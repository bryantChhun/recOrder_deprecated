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

from src.DataStructures.BackgroundData import BackgroundData
from src.Processing.ReconOrder import ReconOrder


def snap_channel(channel: str, gateway: JavaGateway):
    """
    Snaps an image on micromanager and returns the memmap data

    :param channel: preset for the configuration group "channel"
    :param gateway: py4j gateway
    :return: np.ndarray-like data
    """
    mmc = gateway.entry_point.getCMMCore()
    mm = gateway.entry_point.getStudio()

    mmc.setConfig('Channel', channel)
    livemanager = mm.getSnapLiveManager()
    livemanager.snap(False)

    data_filename = gateway.entry_point.getFile(channel)
    store = gateway.entry_point.getStore(channel)
    data_pixelshape = (store.x_dim, store.y_dim)
    data_pixeldepth = 8*store.bitdepth
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16
    data = np.memmap(filename=data_filename, dtype=depth, offset=0, shape=data_pixelshape)
    return data

def py4j_snap_and_correct(gateway: JavaGateway):
    #snap states 0,1,2,3,4
    # retrieve images
    # launch simple recon and send to display
    return None

def py4j_collect_background(gateway: JavaGateway, bg_raw: BackgroundData):
    bg_raw.state0 = snap_channel('State0', gateway)
    bg_raw.state1 = snap_channel('State1', gateway)
    bg_raw.state2 = snap_channel('State2', gateway)
    bg_raw.state3 = snap_channel('State3', gateway)
    bg_raw.state4 = snap_channel('State4', gateway)
    processor = ReconOrder()
    processor.frames = 5

    #connect pipeline to GUI if necessary

    #assign intensity states
    processor.state = (0, bg_raw.state0)
    processor.state = (1, bg_raw.state1)
    processor.state = (2, bg_raw.state2)
    processor.state = (3, bg_raw.state3)
    processor.state = (4, bg_raw.state4)

    # construct and assign stokes to bg_raw
    processor.compute_stokes()
    bg_raw.s0 = processor.s0
    bg_raw.s1 = processor.s1
    bg_raw.s2 = processor.s2
    bg_raw.s3 = processor.s3

    # construct and assign physical to bg_raw
    processor.compute_physical()
    bg_raw.I_trans = processor.I_trans
    bg_raw.retard = processor.retard
    bg_raw.polarization = processor.polarization
    bg_raw.scattering = processor.scattering
    bg_raw.azimuth = processor.azimuth
    return None



def py4j_calibrate_lc(gateway: JavaGateway):
    #create processing module
    #call CalibrateLC processor


    return None

