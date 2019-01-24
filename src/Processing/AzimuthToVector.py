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

import cv2

def convert_to_vector(azimuth: np.array, retardance: np.array, stride_x: int = 1, stride_y: int = 1) -> np.array:
    """
    This function converts an "azimuth" (radian) array into a vector array
    Method:
        1) create empty vector of length = size of input array
        2) create meshgrid coordinates to map x-y positions onto the image
        3) calculate new coordinates (by adjusting 2nd of every pair of coordinates) based on input angle-array

    *** timed at roughly 5ms compute, after 50ms initialization ***

    :param azimuth: np array of angles in radians
    :param stride_x: if converting an averaging result, expand the image by a factor
    :param stride_y: if converting an averaging result, expand the image by a factor
    :return:
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

    if stride_x > 1:
        pos[0::2,0] -= stride_x
        pos[1::2,0] += stride_x

    #adjust second coordinate to represent azimuth angle
    azimuth_flat = azimuth.flatten()
    xdiff = pos[1::2,0] - pos[0::2,0]
    pos[1::2, 0] += retardance[::] * np.cos(azimuth_flat[::]) - xdiff[::]
    pos[1::2, 1] += retardance[::] * np.sin(azimuth_flat[::])

    #subtract and add kernel offsets to "stretch" the line
    # if avg_offset_x > 1:
    #     pos[0::2,0] -= avg_offset_x
    #     pos[1::2,0] += avg_offset_x
    # if avg_offset_y > 1:
    #     pos[0::2,1] -= avg_offset_y
    #     pos[1::2,1] += avg_offset_y

    return pos

def compute_average(s1, s2, s3, kernel: str = '1x1', flipPol=False) -> np.array:
    """
    This function computes the average azimuth_vector from the constituent stokes vectors

    *** timed at roughly 43ms compute ***

    :param s1: stokes image of type np.ndarray
    :param s2: stokes image of type np.ndarray
    :param kernel: dims over which averaging occurs.
    :return:
    """
    kernel_dict = {'1x1': (1, 1),
                   '3x3': (3, 3),
                   '5x5': (5, 5),
                   '7x7': (7, 7),
                   '9x9': (9, 9),
                   '11x11': (11, 11)}
    x = kernel_dict[kernel][0]
    y = kernel_dict[kernel][1]
    x_offset = int((x-1)/2)
    y_offset = int((y-1)/2)

    s1_avg = cv2.blur(s1, (x,y))[x_offset:-x_offset-1:x, y_offset:-y_offset-1:y]
    s2_avg = cv2.blur(s2, (x,y))[x_offset:-x_offset-1:x, y_offset:-y_offset-1:y]
    s3_avg = cv2.blur(s3, (x,y))[x_offset:-x_offset-1:x, y_offset:-y_offset-1:y]

    if flipPol == 'rcp':
        azimuth = (0.5 * np.arctan2(-s1_avg, s2_avg) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
    else:
        azimuth = (0.5 * np.arctan2(s1_avg, s2_avg) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
    retard_avg = np.arctan2(np.sqrt(s1 ** 2 + s2 ** 2), s3) (2 * np.pi)

    return convert_to_vector(azimuth - (0.5 * np.pi),retardance=retard_avg, stride_x=x, stride_y=y)

