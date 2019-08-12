# bchhun, {2019-07-29}

import numpy as np
from datetime import datetime
import time


def snap_and_get_image(entry_point, mm_):
    """
    Snaps an image on micromanager and returns the memmap data

    Parameters
    ----------
    entry_point : py4j entry point
    mm_ : micro-manager studio

    Returns
    -------
    ndarray
    """
    ep = entry_point
    mm = mm_
    ep.clearQueue()

    # snap image
    live_manager = mm.getSnapLiveManager()
    live_manager.snap(True)

    # we need a monitor to be sure file is written
    start = datetime.now()
    ct = 0
    meta = ep.getLastMeta()
    # while not gateway.entry_point.fileExists(channel):
    while not meta:
        time.sleep(0.0001)
        ct += 1
        meta = ep.getLastMeta()
        if ct >= 10000:
            raise FileExistsError("timeout waiting for file exists")
    stop = datetime.now()
    print("time to check fileExists = %06d" % (stop - start).microseconds)

    # retrieve filepath from metadatastore
    data_filename = meta.getFilepath()
    data_buffer_position = meta.getBufferPosition()
    data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixeldepth = 8 * meta.getBitDepth()
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16

    data = np.memmap(filename=data_filename, dtype=depth, offset=data_buffer_position, shape=data_pixelshape)

    if data is None:
        print("data is none")

    return data


def get_image_by_channel_name(channel_name, ep):
    meta = ep.getLastMetaByChannelName(channel_name)

    # retrieve filepath from metadatastore
    data_filename = meta.getFilepath()
    data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixeldepth = 8 * meta.getBitDepth()
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16

    data = np.memmap(filename=data_filename, dtype=depth, offset=0, shape=data_pixelshape)

    if data is None:
        print("data is none")

    return data


def set_lc(mmc, waves: float, device_property: str):
    """
    puts a value on LCA or LCB
    :param waves: float
        value in radians [0.001, 1.6]
    :param device_property: str
        'LCA' or 'LCB'
    :return: None
    """
    if waves > 1.6 or waves < 0.001:
        raise ValueError("waves must be float, greater than 0.001 and less than 1.6")
    mmc.setProperty('MeadowlarkLcOpenSource', device_property, str(waves))
    mmc.waitForDevice('MeadowlarkLcOpenSource')


def get_lc(mmc, device_property: str) -> float:
    """
    getter for LC value
    :param device_property: str
        'LCA' or 'LCB'
    :return: float
    """
    return float(mmc.getProperty('MeadowlarkLcOpenSource', device_property))


def define_lc_state(mmc, PROPERTIES, device_property: str):
    """
    defines the state based on current LCA - LCB settings
    :param device_property: str
        'State0', 'State1', 'State2' ....
    :return: None
    """
    lca_ext = get_lc(mmc, PROPERTIES['LCA'])
    lcb_ext = get_lc(mmc, PROPERTIES['LCB'])
    print("setting LCA = "+str(lca_ext))
    print("setting LCB = "+str(lcb_ext))
    print("\n")
    mmc.setProperty('MeadowlarkLcOpenSource', device_property, 0)
    mmc.waitForDevice('MeadowlarkLcOpenSource')


def set_lc_state(mmc, device_property: str):
    """
    sets the state based on previously defined values
    :param device_property: str
        'State0', 'State1', 'State2' ....
    :return: None
    """
    mmc.setProperty('MeadowlarkLcOpenSource', device_property, 1)
    mmc.waitForDevice('MeadowlarkLcOpenSource')


def snap_and_retrieve(entry_point):
    """
    use snap/live manager to snap an image then return image
    :return: np.ndarray
    """
    mm = entry_point.getStudio()

    mm.live().snap(True)

    meta = entry_point.getLastMeta()
    # meta is not immediately available -> exposure time + lc delay
    while meta is None:
        meta = entry_point.getLastMeta()

    data = np.memmap(meta.getFilepath(), dtype="uint16", mode='r+', offset=0,
                     shape=(meta.getxRange(), meta.getyRange()))

    return data