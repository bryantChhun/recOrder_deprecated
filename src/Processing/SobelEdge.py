#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/4/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import cv2

'''
This module exists as a placeholder for future, simple processing declarations.

'''

def rotate_and_sobel(image, deg):
    return cv2_rotate( cv2_sobel_edge_with_binary(image), deg)

def cv2_rotate(image, degree):
    rows, cols = image.shape
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), degree, 1)
    dest = cv2.warpAffine(image, M, (cols, rows))
    return dest

def cv2_sobel_edge_with_binary(image):

    k=3
    t=5000
    blur = cv2.GaussianBlur(image, (k,k),0)

    (t, binary) = cv2.threshold(blur,t, 65534, cv2.THRESH_BINARY_INV)

    grad_x = cv2.Sobel(binary, cv2.CV_16U, 2, 0)
    grad_y = cv2.Sobel(binary, cv2.CV_16U, 0, 2)

    edge = cv2.bitwise_or(grad_x, grad_y)
    return edge