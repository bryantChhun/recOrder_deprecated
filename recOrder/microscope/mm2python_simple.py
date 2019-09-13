# bchhun, {2019-07-29}

import numpy as np
from datetime import datetime
import time, os
import tifffile
import json

from recOrder.acquisition import AcquisitionBase
from recOrder.datastructures import IntensityData
from recOrder.analysis.ReconstructOrder import ReconOrder


# ============================================================
# ===================== acquisition methods ==================

class SnapAndRetrieve(AcquisitionBase):

    @AcquisitionBase.emitter(channel=4)
    def snap_and_retrieve(self, entry_point):
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


def snap_and_get_image(entry_point, channel=None):
    """
    Snaps an image on micromanager and returns the memmap data

    Parameters
    ----------
    entry_point : py4j entry point
    channel : retrieve on specific channel

    Returns
    -------
    ndarray
    """
    ep = entry_point
    mm = ep.getStudio()
    # ep.clearAll()

    # snap image
    mm.live().snap(True)

    if channel:
        meta = ep.getLastMetaByChannelName(channel)
        ct = 0
        while not meta:
            time.sleep(0.0001)
            ct += 1
            meta = ep.getLastMetaByChannelName(channel)
            if ct >= 5000:
                # print("FileExistsError: timeout waiting for file by channel %s exists" % channel)
                # return None
                raise FileExistsError("timeout waiting for file by channel %s exists" % channel)
    else:
        ct = 0
        meta = ep.getLastMeta()
        while not meta:
            time.sleep(0.0001)
            ct += 1
            meta = ep.getLastMeta()
            if ct >= 5000:
                raise FileExistsError("timeout waiting for file exists")
                # print("FileExistsError: timeout waiting for file exists")
                # return None

    # retrieve filepath from metadatastore
    data_filename = meta.getFilepath()
    data_buffer_position = meta.getBufferPosition()
    data_pixelshape = (meta.getxRange(), meta.getyRange())
    data_pixeldepth = meta.getBitDepth()

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


#  set channel, snap channel, get channel sequence
def set_and_snap_channel(channel, entry_point):

    set_channel(channel, entry_point)

    # data = get_image_by_channel_name(channel, ep)
    data = snap_and_get_image(entry_point, channel=channel)

    return data


def set_channel(channel, entry_point):

    mmc = entry_point.getCMMCore()

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
    data_pixeldepth = meta.getBitDepth()
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

# ============================================================
# =========== Reconstruct Order methods  =====================

# for hardware setting
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


# for collection and compute

def py4j_snap_and_correct(gateway, bg):
    int_dat = IntensityData()
    int_dat.add_image(set_and_snap_channel('State0', gateway))
    int_dat.add_image(set_and_snap_channel('State1', gateway))
    int_dat.add_image(set_and_snap_channel('State2', gateway))
    int_dat.add_image(set_and_snap_channel('State3', gateway))
    int_dat.add_image(set_and_snap_channel('State4', gateway))

    proc = ReconOrder()
    stk_obj = proc.compute_stokes(int_dat)

    corrected = proc.correct_background(stk_obj, bg)
    return corrected


def py4j_collect_background(gateway, bg_raw, swing, wavelength, black_level, save_path=None, averaging: int = 5, ):

    # we assume that the image for channel=State0 is the same as that for all other states
    # meta = gateway.entry_point.getStore('State0')
    # data_pixelshape = (meta.getxRange(), meta.getyRange())

    data_pixelshape = (2048, 2048)

    #assign intensity states
    bg_raw.add_image(np.mean([set_and_snap_channel('State0', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([set_and_snap_channel('State1', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([set_and_snap_channel('State2', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([set_and_snap_channel('State3', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    bg_raw.add_image(np.mean([set_and_snap_channel('State4', gateway).flatten() for i in range(0, averaging)], axis=0)\
        .reshape(data_pixelshape))
    print("all states snapped")

    # this instance will not display because its signals are not connected by Builder
    processor = ReconOrder()
    processor.frames = 5
    processor.swing = swing
    processor.wavelength = wavelength
    processor.compute_inst_matrix()

    # construct and assign stokes to bg_raw
    bg_stks = processor.compute_stokes(bg_raw)
    bg_raw.assign_stokes(bg_stks)

    # construct and assign physical to bg_raw
    phys_obj = processor.compute_physical(bg_stks)
    bg_raw.assign_physical(phys_obj)

    # write to disk
    if save_path:
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        folder_name = "BG_%04d_%02d%02d_%02d%02d_%02d" % (datetime.now().year,
                                                          datetime.now().month,
                                                          datetime.now().day,
                                                          datetime.now().hour,
                                                          datetime.now().minute,
                                                          datetime.now().second)
        os.mkdir(os.path.join(save_path, folder_name))
        subfolder_name = "Pos0"
        bg_path = os.path.join(os.path.join(save_path, folder_name), subfolder_name)
        os.mkdir(bg_path)

        # write files to disk
        save_to_disk(bg_path, bg_raw)

        # write metadata to disk
        build_bg_metadata(bg_path, swing, wavelength, black_level, gateway)

    return bg_raw


def save_to_disk(bg_path_, bg_raw_):

    tifffile.imsave(os.path.join(bg_path_, "img_000000000_State0 - Acquired Image_000.tif"), bg_raw_.get_image("IExt"))
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_State1 - Acquired Image_000.tif"), bg_raw_.get_image("I90"))
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_State2 - Acquired Image_000.tif"), bg_raw_.get_image("I135"))
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_State3 - Acquired Image_000.tif"), bg_raw_.get_image("I45"))
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_State4 - Acquired Image_000.tif"), bg_raw_.get_image("I0"))

    tifffile.imsave(os.path.join(bg_path_, "img_000000000_Retardance - Computed Image_000.tif"), bg_raw_.retard)
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_Polarization - Computed Image_000.tif"), bg_raw_.polarization)
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_Transmitted - Computed Image_000.tif"), bg_raw_.I_trans)
    tifffile.imsave(os.path.join(bg_path_, "img_000000000_Azimuth - Computed Image_000.tif"), bg_raw_.azimuth)


def build_bg_metadata(path, swing, wavelength, black_level, gateway):

    METADATA_TEMPLATE = {'InitialPositionList': None,
                         'UUID': '029893fe-6f12-4bae-955a-853ebb9c9782',
                         '~ Swing (fraction)': 0.03,
                         '~ Processed Using': '5-Frame',
                         'PolScope_Algorithm': 'Birefringence',
                         'Date': '2019-06-12',
                         '~ Wavelength (nm)': 530,
                         'MetadataVersion': 10,
                         'PositionIndex': 0,
                         'Width': 2048,
                         'PixelAspect': 1,
                         '~ Acquired Using': '5-Frame',
                         'ROI': [0, 0, 2048, 2048],
                         'ChNames': ['State0 - Acquired Image',
                                     'State1 - Acquired Image',
                                     'State2 - Acquired Image',
                                     'State3 - Acquired Image',
                                     'State4 - Acquired Image'],
                         'PolScope_Plugin_Version': 3.2,
                         'Comment': '',
                         'Height': 2048,
                         'GridColumn': 0,
                         'Frames': 1,
                         'PixelSize_um': 0,
                         'Prefix': 'BG_2019_0612_1443_1',
                         'Channels': 7,
                         'Source': 'Micro-Manager',
                         'CustomIntervals_ms': [],
                         'ChColors': '[-1,-1,-1,-16711936,-16711681,-65536,-16776961]',
                         'PolScope_API_Build': '09-28-2017',
                         '~ Retardance Ceiling (nm)': 20,
                         'View_TYPE': 'Acquisition',
                         'Slices': 1,
                         '~ BlackLevel': 4,
                         'Interval_ms': 0,
                         'UserName': 'labelfree',
                         'Depth': 2,
                         'PixelType': 'GRAY16',
                         'Time': '2019-06-12 14:43:26 -0700',
                         'z-step_um': 0,
                         'ChContrastMin': [0, 0, 0, 0, 0, 0, 0],
                         'SlicesFirst': False,
                         'MicroManagerVersion': '2.0-beta',
                         'IJType': 1,
                         'GridRow': 0,
                         '~ Mirror': 'No',
                         'PolScope_Info': 'OpenPolScope: 3.20 API Built-Date: 09-28-2017',
                         'KeepShutterOpenChannels': True,
                         'BitDepth': 16,
                         'ComputerName': 'CZLASX-01',
                         '~ Azimuth Reference (degrees)': 0,
                         'KeepShutterOpenSlices': False,
                         'TimeFirst': False,
                         '~ Background': 'No Background',
                         'ChContrastMax': [65536, 65536, 65536, 65536, 65536, 65536, 65536],
                         'Positions': 1,
                         'Directory': ''}

    # change values to reflect non-template
    # need to snap an image and use this info for meta
    summary = {'Summary': METADATA_TEMPLATE}

    # change polscope values
    summary['Summary']['~ Acquired Using'] = '5-Frame'
    summary['Summary']['~ Background'] = 'No Background'
    summary['Summary']['~ BlackLevel'] = black_level
    summary['Summary']['~ Mirror'] = 'No'
    summary['Summary']['~ Swing (fraction)'] = swing
    summary['Summary']['~ Wavelength (nm)'] = wavelength

    # change hardware values
    mm = gateway.entry_point.getStudio()
    im = mm.getAcquisitionManager().snap()
    metadata = mm.getAcquisitionManager().generateMetadata(im.get(0), True)
    summary['Summary']['BitDepth'] = metadata.getBitDepth()
    summary['Summary']['Height'] = metadata.getROI().getHeight()
    summary['Summary']['Width'] = metadata.getROI().getHeight()

    # json dump it
    with open(os.path.join(path, 'metadata.txt'), 'w+') as outfile:
        print("writing metadata.txt")
        json.dump(summary, outfile)
