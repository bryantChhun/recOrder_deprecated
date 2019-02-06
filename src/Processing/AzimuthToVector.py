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

import cv2


def convert_to_vector(azimuth: np.array,
                      retardance: np.array,
                      stride_x: int = 1,
                      stride_y: int = 1,
                      length: Union[int, float] = 10) -> np.array:
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
    pos = np.zeros((2*xdim*ydim, 2), dtype=np.float32)

    #create coordinate spacing for x-y
    # double the num of elements by doubling x sampling
    xspace = np.linspace(0, stride_x * xdim, 2 * xdim)
    yspace = np.linspace(0, stride_y * ydim, ydim)
    xv, yv = np.meshgrid(xspace, yspace)

    #assign coordinates (pos) to all pixels
    pos[:, 0] = xv.flatten()
    pos[:, 1] = yv.flatten()

    #pixel midpoints are the first x-value of positions
    midpt = np.zeros((xdim*ydim, 2), dtype=np.float32)
    midpt[:, 0] = pos[0::2, 0]
    midpt[:, 1] = pos[0::2, 1]

    #rotate coordinates about midpoint to represent azimuth angle and length
    azimuth_flat = azimuth.flatten()
    retard_flat = retardance.flatten()
    pos[0::2, 0] = midpt[:, 0] - (stride_x/2) * length * retard_flat * np.cos(azimuth_flat)
    pos[0::2, 1] = midpt[:, 1] - (stride_y/2) * length * retard_flat * np.sin(azimuth_flat)
    pos[1::2, 0] = midpt[:, 0] + (stride_x/2) * length * retard_flat * np.cos(azimuth_flat)
    pos[1::2, 1] = midpt[:, 1] + (stride_y/2) * length * retard_flat * np.sin(azimuth_flat)

    return pos


def compute_average(s1,
                    s2,
                    s3,
                    kernel: tuple = (1,1),
                    length: Union[int, float] = 10,
                    flipPol=False) -> np.array:
    """
    This function computes the average azimuth_vector from the constituent stokes vectors

    *** timed at roughly 43ms compute ***

    :param s1: stokes image of type np.ndarray
    :param s2: stokes image of type np.ndarray
    :param kernel: dims over which averaging occurs.
    :param length:
    :param flipPol:
    :return:
    """
    x = kernel[0]
    y = kernel[1]
    x_offset = int((x-1)/2)
    y_offset = int((y-1)/2)

    s1_avg = cv2.blur(s1, (x,y))[x_offset:-x_offset-1:x, y_offset:-y_offset-1:y]
    s2_avg = cv2.blur(s2, (x,y))[x_offset:-x_offset-1:x, y_offset:-y_offset-1:y]
    s3_avg = cv2.blur(s3, (x,y))[x_offset:-x_offset-1:x, y_offset:-y_offset-1:y]

    if flipPol == 'rcp':
        azimuth_avg = (0.5 * np.arctan2(-s1_avg, s2_avg) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
    else:
        azimuth_avg = (0.5 * np.arctan2(s1_avg, s2_avg) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
    retard_avg = np.arctan2(np.sqrt(s1_avg ** 2 + s2_avg ** 2), s3_avg) / (2 * np.pi)

    vectors = convert_to_vector(azimuth_avg - (0.5 * np.pi), retardance=retard_avg, stride_x=x, stride_y=y, length=length)

    return azimuth_avg, retard_avg, vectors


def convert_to_vector_map(azimuth,
                          retardance,
                          stride_x: int = 1,
                          stride_y: int = 1,
                          length: Union[int, float] = 10) -> np.array:
    out = np.array(list(zip(azimuth.flatten(), retardance.flatten())))
    return out.reshape(azimuth.shape[0], azimuth.shape[0], 2)

