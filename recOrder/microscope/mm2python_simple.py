# bchhun, {2019-07-29}

import numpy as np
from datetime import datetime
import time

from recOrder.datastructures import IntensityData
from recOrder.datastructures import StokesData
from recOrder.datastructures import PhysicalData
from recOrder.datastructures import BackgroundData


# ============================================================
# ===================== acquisition methods ==================

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


def snap_channel(channel, entry_point):
    ep = entry_point
    ep.clearQueue()
    mm = ep.getStudio()

    set_channel(channel, entry_point)

    mm.getSnapLiveManager().snap(True)

    data = get_image_by_channel_name(channel, ep)

    return data


def set_channel(channel, entry_point):

    mmc = entry_point.getCMMCore()

    # micro-manager is slow (not mm2python). we need a monitor to be sure it gets set....
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


def get_image_by_channel_name(channel_name, ep):

    meta = ep.getLastMetaByChannelName(channel_name)
    ct = 0
    while not meta:
        time.sleep(0.0001)
        ct += 1
        meta = ep.getLastMetaByChannelName(channel_name)
        if ct >= 10000:
            raise FileExistsError("timeout waiting for file exists")

    # retrieve filepath from metadatastore
    data_filename = meta.getFilepath()
    data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixeldepth = 8 * meta.getBitDepth()
    offset = meta.getBufferPosition()
    if data_pixeldepth == 16:
        depth = np.uint16
    elif data_pixeldepth == 8:
        depth = np.uint8
    else:
        depth = np.uint16

    data = np.memmap(filename=data_filename, dtype=depth, offset=offset, shape=data_pixelshape)

    if data is None:
        print("data is none")

    return data


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

# ============================================================
# =========== Reconstruct Order methods  =====================


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


def py4j_collect_background(gateway, bg_raw, averaging: int = 5):
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

    bg_raw.add_image(np.mean([snap_channel('State0', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([snap_channel('State1', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([snap_channel('State2', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([snap_channel('State3', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([snap_channel('State4', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))

    # processor = ReconOrder()
    # processor.frames = 5
    # processor.compute_inst_matrix()
    # processor.swing = 0.1
    print("all states snapped")

    #assign intensity states
    int_obj = IntensityData()
    int_obj.channel_names = ['IExt', 'I0', 'I45', 'I90', 'I135']
    int_obj.add_image(bg_raw.get_image('IExt'))
    int_obj.add_image(bg_raw.get_image('I0'))
    int_obj.add_image(bg_raw.get_image('I45'))
    int_obj.add_image(bg_raw.get_image('I90'))
    int_obj.add_image(bg_raw.get_image('I135'))
    # print("all states assigned to properties")

    # construct and assign stokes to bg_raw
    stk_obj = processor.compute_stokes(bg_raw)
    bg_raw.assign_stokes(stk_obj)
    # print("stokes computed")
    # bg_raw.s0 = stk_obj.s0
    # bg_raw.s1 = stk_obj.s1
    # bg_raw.s2 = stk_obj.s2
    # bg_raw.s3 = stk_obj.s3
    # print('stokes vectors assigned to background object')

    # construct and assign physical to bg_raw
    phys_obj = processor.compute_physical(stk_obj)
    bg_raw.assign_physical(phys_obj)
    # print("physical computed")
    # bg_raw.I_trans = phys_obj.I_trans
    # bg_raw.retard = phys_obj.retard
    # bg_raw.polarization = phys_obj.polarization
    # bg_raw.scattering = phys_obj.scattering
    # bg_raw.azimuth = phys_obj.azimuth
    # print("physical assigned to background object")

    # write to disk
    # create a folder with a name
    # this write should iterate through all BG data stokes? and create a .npy file for each?

    # update UI field to reflect new folder
    # in reconOrderUI we will have the text field trigger another method that
    #   will read the .npy files and update ReconOrderUI's self.Background object

    return bg_raw