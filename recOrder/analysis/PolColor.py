import cv2
import numpy as np
import bisect
import warnings
from matplotlib.colors import hsv_to_rgb


def color_wheel(retardance, orientation, ret_scale = 30):
    """

    :param retardance: unscaled in nm
    :param orientation: in radians
    :param ret_scale: max retardance to display
    :return:
    """
    Hexport = (orientation/np.pi)
    Sexport = np.ones_like(Hexport)
    Vexport = retardance/ret_scale
    Vexport[Vexport >= 1] = 1
    Vexport[Vexport <= 0] = 0
    HSV = np.dstack((Hexport, Sexport, Vexport))
    Cmapexport = hsv_to_rgb(HSV)
    return Cmapexport

def PolColor(s0, retardance, orientation, polarization, norm=True):
    """ Generate colormaps with following mappings, where H is Hue, S is Saturation, and V is Value.
        I_azi_ret_trans: H=Orientation, S=retardance, V=Brightfield.
        I_azi_ret: H=Orientation, V=Retardance.
        I_azi_pol: H=Orientation, V=Polarization.
    """

    if norm:
        retardance = imadjust(retardance, tol=1, bit=8)
        s0 = imadjust(s0, tol=1, bit=8)
        polarization = imadjust(polarization, tol=1, bit=8)
        # retardance = cv2.convertScaleAbs(retardance, alpha=(2**8-1)/np.max(retardance))
        # s0 = cv2.convertScaleAbs(s0, alpha=(2**8-1)/np.max(s0))
    else:
        #TODO: make scaling factors parameters in the config
        retardance = cv2.convertScaleAbs(retardance, alpha=50)
        s0 = cv2.convertScaleAbs(s0, alpha=100)
        polarization = cv2.convertScaleAbs(polarization, alpha=2000)
#    retardance = histequal(retardance)

    orientation = cv2.convertScaleAbs(orientation, alpha=1)
#    retardAzi = np.stack([orientation, retardance, np.ones(retardance.shape).astype(np.uint8)*255],axis=2)
    I_azi_ret_trans = np.stack([orientation, retardance, s0], axis=2)
    I_azi_ret = np.stack([orientation, np.ones(retardance.shape).astype(np.uint8) * 255, retardance], axis=2)
    I_azi_scat = np.stack([orientation, np.ones(retardance.shape).astype(np.uint8) * 255, polarization], axis=2)
    I_azi_ret_trans = cv2.cvtColor(I_azi_ret_trans, cv2.COLOR_HSV2RGB)
    I_azi_ret = cv2.cvtColor(I_azi_ret, cv2.COLOR_HSV2RGB)
    I_azi_scat = cv2.cvtColor(I_azi_scat, cv2.COLOR_HSV2RGB)  #
#    retardAzi = np.stack([orientation, retardance],axis=2)
    return I_azi_ret_trans, I_azi_ret, I_azi_scat


def imadjust(src, tol=1, bit=16, vin=[0, 2 ** 16 - 1]):
    """Python implementation of "imadjust" from MATLAB for stretching intensity histogram. Slow
    Parameters
    ----------
    src : array
        input image
    tol : int
        tolerance in [0, 100]
    bit : int
        output bit depth. 8 or 16
    vin : list
        src image bounds
    Returns
    -------
    """
    # TODO: rewrite using np.clip

    bitTemp = 16  # temporary bit depth for calculation.
    vout = (0, 2 ** bitTemp - 1)
    if src.dtype == 'uint8':
        bit = 8

    src = imBitConvert(src, norm=True)  # rescale to 16 bit
    srcOri = np.copy(src)  # make a copy of source image
    if len(src.shape) > 2:
        src = np.mean(src, axis=2)
        src = imBitConvert(src, norm=True)  # rescale to 16 bit

    tol = max(0, min(100, tol))

    if tol > 0:
        # Compute in and out limits
        # Histogram
        hist = np.histogram(src, bins=list(range(2 ** bitTemp)), range=(0, 2 ** bitTemp - 1))[0]

        # Cumulative histogram
        cum = hist.copy()
        for i in range(1, 2 ** bitTemp - 1): cum[i] = cum[i - 1] + hist[i]

        # Compute bounds
        total = src.shape[0] * src.shape[1]
        low_bound = total * tol / 100
        upp_bound = total * (100 - tol) / 100
        vin[0] = bisect.bisect_left(cum, low_bound)
        vin[1] = bisect.bisect_left(cum, upp_bound)

    # Stretching
    if vin[1] == vin[0]:
        warnings.warn("Tolerance is too high. No contrast adjustment is perfomred")
        dst = srcOri
    else:
        if len(srcOri.shape) > 2:
            dst = np.array([])
            for i in range(0, srcOri.shape[2]):
                src = srcOri[:, :, i]
                src = src.reshape(src.shape[0], src.shape[1], 1)
                vd = linScale(src, vin, vout)
                if dst.size:
                    dst = np.concatenate((dst, vd), axis=2)
                else:
                    dst = vd
        else:
            vd = linScale(src, vin, vout)
            dst = vd
    dst = imBitConvert(dst, bit=bit, norm=True)
    return dst

def imBitConvert(im,bit=16, norm=False, limit=None):
    """covert bit depth of the image
    Parameters
    ----------
    im : array
        input image
    bit : int
        output bit depth. 8 or 16
    norm : bool
        scale the image intensity range specified by limit to the full bit depth if True.
        Use min and max of the image if limit is not provided
    limit: list
        lower and upper limits of the image intensity
    Returns
        im : array
        converted image
    -------
    """
    im = im.astype(np.float32, copy=False) # convert to float32 without making a copy to save memory
    if norm: # local or global normalization (for tiling)
        if not limit: # if lmit is not provided, perform local normalization, otherwise global (for tiling)
            limit = [np.nanmin(im[:]), np.nanmax(im[:])] # scale each image individually based on its min and max
        im = (im-limit[0])/(limit[1]-limit[0])*(2**bit-1)

    im = np.clip(im, 0, 2**bit-1) # clip the values to avoid wrap-around by np.astype
    if bit==8:
        im = im.astype(np.uint8, copy=False) # convert to 8 bit
    else:
        im = im.astype(np.uint16, copy=False) # convert to 16 bit
    return im

def linScale(src,vin, vout):
    """Scale the source image according to input and output ranges
    Parameters
    ----------
    src
    vin
    vout
    Returns
    -------
    """
    scale = (vout[1] - vout[0]) / (vin[1] - vin[0])
    vs = src-vin[0]
    vs[src<vin[0]]=0
    vd = vs*scale + 0.5 + vout[0]
    vd[vd>vout[1]] = vout[1]
    return vd