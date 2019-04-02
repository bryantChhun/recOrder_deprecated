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
    pos[:, :, 0] = (stride_x//2 + 1) * length * retardance * np.cos(azimuth)
    pos[:, :, 1] = (stride_y//2 + 1) * length * retardance * np.sin(azimuth)

    return pos


def compute_average(stk_img : StokesData,
                    kernel, range_x, range_y,
                    func
                    ) -> np.array:
    x, y = kernel, kernel
    x_offset = int((x-1)/2)
    y_offset = int((y-1)/2)
    kernel = np.ones(shape=(x, y)) / (x * y)

    # orig_data is vector data of image-like (N,M,2) shape

    # calculate average based on stokes
    avg_stokes = StokesData()
    avg_stokes.s0 = stk_img.s0
    avg_stokes.s1 = signal.convolve2d(stk_img.s1, kernel, mode='same', boundary='wrap')
    avg_stokes.s2 = signal.convolve2d(stk_img.s2, kernel, mode='same', boundary='wrap')
    avg_stokes.s3 = signal.convolve2d(stk_img.s3, kernel, mode='same', boundary='wrap')

    # calculate the new physical based on average stokes
    avg_phys = func.compute_physical(avg_stokes)
    new_vect = np.zeros(shape=(range_x, range_y, 2))
    new_vect[:, :, 0] = avg_phys.azimuth_vector[:, :, 0]
    new_vect[:, :, 1] = avg_phys.azimuth_vector[:, :, 1]

    # slice the averaged data based on kernel
    out_vect = new_vect[x_offset:-x_offset:x, y_offset:-y_offset:y]

    return out_vect


def compute_length():
    return None