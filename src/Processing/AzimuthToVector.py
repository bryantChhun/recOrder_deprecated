#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :1/20/19
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import numpy as np
from typing import Union

from scipy import signal

from src.DataStructures import StokesData


def convert_to_vector(azimuth: np.array,
                      retardance: np.array,
                      stride_x: int = 1,
                      stride_y: int = 1,
                      length: Union[int, float] = 1) -> np.array:
    """
    This function converts an "azimuth" (radian) array into a vector array
    Method:
        1) create empty vector of length = size of input array
        2) create meshgrid coordinates to map x-y positions onto the image
        3) calculate new coordinates (by adjusting 2nd of every pair of coordinates) based on input angle-array

    *** timed at roughly 5ms compute, after 50ms initialization ***

    :param azimuth: ndarray of angles in radians
    :param retardance: ndarray of fractions of a wavelength
    :param stride_x: if converting an averaging result, expand the image by a factor
    :param stride_y: if converting an averaging result, expand the image by a factor
    :param length:
    :return: vector ndarray of shape (N, 2)
    """

    xdim = azimuth.shape[0]
    ydim = azimuth.shape[1]

    #create empty vector of necessary shape
    # every pixel has 2 coordinates,
    pos = np.zeros((xdim, ydim, 2), dtype=np.float32)
    pos[:, :, 0] = (stride_x//2) * length * retardance * np.cos(azimuth)
    pos[:, :, 1] = (stride_y//2) * length * retardance * np.sin(azimuth)

    return pos


def compute_average(stk_img : StokesData,
                    kernel : int = 1,
                    length: Union[int, float] = 1,
                    flipPol=False) -> np.array:

    x, y = kernel, kernel
    x_offset = int((x-1)/2)
    y_offset = int((y-1)/2)

    # if (x, y) == (1, 1):
    #     self.vectors = self._original_data
    #     return
    #     # return "calling original data"

    kernel = np.ones(shape=(x, y)) / (x * y)

    s1_avg = signal.convolve2d(stk_img.s1[:, :, 0], kernel, mode='same', boundary='wrap')
    s2_avg = signal.convolve2d(stk_img.s2[:, :, 1], kernel, mode='same', boundary='wrap')
    s3_avg = signal.convolve2d(stk_img.s3[:, :, 1], kernel, mode='same', boundary='wrap')

    if flipPol == 'rcp':
        azimuth_avg = (0.5 * np.arctan2(-s1_avg, s2_avg) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
    else:
        azimuth_avg = (0.5 * np.arctan2(s1_avg, s2_avg) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
    retard_avg = np.arctan2(np.sqrt(s1_avg ** 2 + s2_avg ** 2), s3_avg) / (2 * np.pi)

    # self.vectors = output_mat[x_offset:range_x - x_offset:x, y_offset:range_y - y_offset:y]
    # self.length = self._length

    vectors = convert_to_vector(azimuth_avg - (0.5 * np.pi), retardance=retard_avg, stride_x=x, stride_y=y, length=length)

    return azimuth_avg, retard_avg, vectors

