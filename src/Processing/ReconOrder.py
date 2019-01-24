#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/4/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6

import numpy as np
import cv2

from src.Processing.ReconExceptions import InsufficientDataError, InvalidFrameNumberDeclarationError, InvalidBackgroundObject
from src.Processing.AzimuthToVector import convert_to_vector, compute_average

from datetime import datetime

import weakref

'''
ReconOrder contains all methods to reconstruct polarization images.
    The number of frames (4 or 5 frame acquisition), and each image for each frame
    must be explicitly set or errors will be thrown during reconstruction.
    
    The order of operations should be as such:
    1) Instantiate
    2) Set number of frames (4 or 5)
    3) Set states, where each "state" is an image.  The order matters:
        state[0] = I_ext
        state[1] = I_90
        state[2] = I_135
        state[3] = I_45
        state[4] = I_0
    4) Call compute Stokes
    5) Call reconstruct_img
'''

class ReconOrder(object):

    # recon_complete = pyqtSignal(object)
    inst_mat_inv = None

    def __init__(self):
        super().__init__()
        self._states = [None] * 5
        self._frames = None

        # self.img_raw_bg = img_raw_bg
        # self.n_chann = np.shape(img_raw_bg)[0]
        self.height = None
        self.width = None

        # self.method = method
        #swing is hard coded based on metadata info.
        swing = 0.1
        self.swing = swing*2*np.pi # covert swing from fraction of wavelength to radian
        self.wavelength = 532
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (100,100))

        self.flipPol = None

        # Stokes vectors
        self.s0 = None
        self.s1 = None
        self.s2 = None
        self.s3 = None

        # normalized stokes
        self.I_trans = None
        self.polarization = None
        self.A = None
        self.B = None
        self.dAB = None

        self.retard = None
        self.azimuth = None
        self.scattering = None
        self.azimuth_degree = None

        self.azimuth_vector = None

        self.local_gauss = None

    @property
    def frames(self) -> int:
        return self._frames

    @frames.setter
    def frames(self, num_frames=4):
        if num_frames != 4 and num_frames != 5:
            raise InvalidFrameNumberDeclarationError("support only 4 or 5 frame reconstructions")
        else:
            self._frames = num_frames

    @property
    def state(self, polstate: int) -> np.array:
        return self._states[polstate]

    @state.setter
    def state(self, statemap: tuple):
        if len(statemap) != 2:
            raise ValueError("invalid state parameter: state setter receives tuple of (index, image)")
        self._states[statemap[0]] = statemap[1]
        self.height = self._states[statemap[0]].shape[0]
        self.width = self._states[statemap[0]].shape[1]

    # def set_state(self, state: int, img: np.array):
    #     """
    #     Assigns an image to a list of states.  Each image corresponds to one of required polarizations
    #     :param state: list index used for assignment
    #     :param img: 2d numpy array.
    #     :return: None
    #     """
    #     self._states[state] = img
    #     self.height = self._states[state].shape[0]
    #     self.width = self._states[state].shape[1]
    #
    # def get_state(self, state: int) -> np.array:
    #     return self._states[state]

    def correct_background(self, background: object):

        """
        Uses computed result from background images to calculate the correction
        :param background: ReconOrder object that is constructed from background images
        :return: None
        """

        if isinstance(background, ReconOrder):
            self.I_trans = self.I_trans / background.I_trans
            self.polarization = self.polarization / background.polarization
            self.A = self.A - background.A
            self.B = self.B - background.B
            return True
        else:
            raise InvalidBackgroundObject("background parameter must be a ReconOrder object or None (for local Gauss)")

    # def correct_background_localGauss(self):
    #     self.local_gauss = ReconOrder()
    #
    #     self.local_gauss.I_trans = cv2.GaussianBlur(self.I_trans, (401, 401), 0)
    #     self.local_gauss.polarization = cv2.GaussianBlur(self.polarization, (401, 401), 0)
    #     self.local_gauss.A = cv2.GaussianBlur(self.A, (401, 401), 0)
    #     self.local_gauss.B = cv2.GaussianBlur(self.B, (401, 401), 0)
    #     self.local_gauss.dAB = cv2.GaussianBlur(self.dAB, (401, 401), 0)
    #     self.correct_background(self.local_gauss)
    #     return True


    def compute_inst_matrix(self):
        chi = self.swing
        if self._frames == 4:
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        elif self._frames == 5:
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        else:
            raise InvalidFrameNumberDeclarationError('Frames not set to 4 or 5:  Required for calculation of instrument matrix')
        self.inst_mat_inv = np.linalg.pinv(inst_mat)
        # print('instrument matrix calculated, value is : %s', type(self.inst_mat_inv))
        return None

    '''
    #===============================================================================
    #=========  Everything below is taken from Syuan-Ming's reconOrder code ========
    #===============================================================================
    Key notes:
        1) I change all functions to set class properties instead of passing image data
    '''

    # def compute_stokes(self) -> bool:
    #     if self._frames is None or self._frames < 4 or self._frames > 5:
    #         raise InvalidFrameNumberDeclarationError("Number of frames not defined")
    #     for idx, element in enumerate(self._states[:-1]):
    #         if element is None:
    #             raise InsufficientDataError("No image loaded for index = %01d" % idx)
    #
    #     I_ext = self._states[0] # Sigma0 in Fig.2
    #     I_90 = self._states[1] # Sigma2 in Fig.2
    #     I_135 = self._states[2] # Sigma4 in Fig.2
    #     I_45 = self._states[3] # Sigma3 in Fig.2
    #
    #     if self._frames == 4:
    #         img_raw = np.stack((I_ext, I_45, I_90, I_135))  # order the channel following stokes calculus convention
    #     elif self._frames == 5:  # if the images were taken using 5-frame scheme
    #         if self._states[4] is None:
    #             raise InsufficientDataError("No image loaded for index = 4")
    #         I_0 = self._states[4]
    #         img_raw = np.stack((I_ext, I_0, I_45, I_90, I_135))  # order the channel following stokes calculus convention
    #
    #     # if self.inst_mat_inv is None:
    #     self.compute_inst_matrix()
    #
    #     img_raw_flat = np.reshape(img_raw,(self._frames, self.height*self.width))
    #     img_stokes_flat = np.dot(self.inst_mat_inv, img_raw_flat)
    #
    #     img_stokes = np.reshape(img_stokes_flat, (img_stokes_flat.shape[0], self.height, self.width))
    #     [self.s0, self.s1, self.s2, self.s3] = [img_stokes[i, :, :] for i in range(0, img_stokes.shape[0])]
    #
    #     self.A = self.s1 / self.s3
    #     self.B = -self.s2 / self.s3
    #     self.I_trans = self.s0
    #     #
    #     self.polarization = np.sqrt(self.s1 ** 2 + self.s2 ** 2 + self.s3 ** 2)/self.s0
    #     return True

    def compute_stokes(self):
        chi = self.swing
        # I_ext = img_raw[0, :, :]  # Sigma0 in Fig.2
        # I_90 = img_raw[1, :, :]  # Sigma2 in Fig.2
        # I_135 = img_raw[2, :, :]  # Sigma4 in Fig.2
        # I_45 = img_raw[3, :, :]  # Sigma3 in Fig.2
        I_ext = self._states[0]  # Sigma0 in Fig.2
        I_90 = self._states[1]  # Sigma2 in Fig.2
        I_135 = self._states[2]  # Sigma4 in Fig.2
        I_45 = self._states[3]  # Sigma3 in Fig.2
        # images = [I_ext, I_90, I_135, I_45]
        # titles = ['I_ext', 'I_90', 'I_135', 'I_45']
        # plot_sub_images(images, titles, self.output_path, 'raw')
        polarization = np.ones((self.height, self.width))  # polorization is always 1 for Jones calculus
        if self._frames == 4:  # if the images were taken using 4-frame scheme
            img_raw = np.stack((I_ext, I_45, I_90, I_135))  # order the channel following stokes calculus convention
            self.n_chann = np.shape(img_raw)[0]
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        elif self._frames == 5:  # if the images were taken using 5-frame scheme
            I_0 = self._states[4]
            img_raw = np.stack((I_ext, I_0, I_45, I_90, I_135))  # order the channel following stokes calculus convention
            self.n_chann = np.shape(img_raw)[0]
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        inst_mat_inv = np.linalg.pinv(inst_mat)
        img_raw_flat = np.reshape(img_raw,(self.n_chann, self.height*self.width))
        img_stokes_flat = np.dot(inst_mat_inv, img_raw_flat)
        img_stokes = np.reshape(img_stokes_flat, (img_stokes_flat.shape[0], self.height, self.width))
        [self.s0, self.s1, self.s2, self.s3] = [img_stokes[i, :, :] for i in range(0, img_stokes.shape[0])]

        self.I_trans = self.s0
        self.polarization = np.sqrt(self.s1 ** 2 + self.s2 ** 2 + self.s3 ** 2) / self.s0
        self.A = self.s1 / self.s3
        self.B = -self.s2 / self.s3


    def reconstruct_img(self, flipPol=False, avg_kernel="1x1"):

        self.retard = np.arctan2(np.sqrt(self.s1 ** 2 + self.s2 ** 2), self.s3)
        self.retard = self.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]

        if flipPol == 'rcp':
            self.flipPol = flipPol
            self.azimuth = (0.5 * np.arctan2(-self.s1, self.s2) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
        else:
            self.flipPol = 'lcp'
            self.azimuth = (0.5 * np.arctan2(self.s1, self.s2) + 0.5 * np.pi)  # make azimuth fall in [0,pi]

        self.scattering = 1 - self.polarization
        self.azimuth_degree = self.azimuth/np.pi*180
        # self.azimuth_vector = convert_to_vector(self.azimuth - (0.5*np.pi))
        self.azimuth_vector = compute_average(self.s1, self.s2, kernel=avg_kernel, flipPol=flipPol)

        self.rescale_bitdepth()

        return True

    def rescale_bitdepth(self):
        print('\t rescaling bitdepth')

        # self.I_trans = imBitConvert(I_trans * 10 ** 3, bit=16, norm=False)  # AU, set norm to False for tiling images
        # self.retard = imBitConvert(retard * 10 ** 3, bit=16)  # scale to pm
        # self.scattering = imBitConvert(self.scattering * 10 ** 4, bit=16)
        # self.azimuth_degree = imBitConvert(self.azimuth_degree * 100, bit=16)  # scale to [0, 18000], 100*degree

        self.I_trans = self.imBitConvert(self.I_trans * 10 ** 3, bit=16, norm=True)  # AU, set norm to False for tiling images
        self.retard = self.imBitConvert(self.retard * 10 ** 3, bit=16)  # scale to pm
        self.scattering = self.imBitConvert(self.scattering * 10 ** 4, bit=16)
        self.azimuth_degree = self.imBitConvert(self.azimuth_degree * 100, bit=16)  # scale to [0, 18000], 100*degree
        # print("bit conversion I_trans (type, min, max, std) = %s %s %s %s" %(str(np.dtype(np.amin(self.I_trans))),
        #                                                               str(np.amin(self.I_trans)),
        #                                                               str(np.amax(self.I_trans)),
        #                                                               str(np.std(self.I_trans)) ))
        # print("bit conversion retard (type, min, max, std) = %s %s %s %s" %(str(np.dtype(np.amin(self.retard))),
        #                                                               str(np.amin(self.retard)),
        #                                                               str(np.amax(self.retard)),
        #                                                               str(np.std(self.retard)) ))
        # print("bit conversion scattering (type, min, max, std) = %s %s %s %s" %(str(np.dtype(np.amin(self.scattering))),
        #                                                               str(np.amin(self.scattering)),
        #                                                               str(np.amax(self.scattering)),
        #                                                               str(np.std(self.scattering)) ))
        # print("bit conversion azimuth_degree (type, min, max, std) = %s %s %s %s" %(str(np.dtype(np.amin(self.azimuth_degree))),
        #                                                               str(np.amin(self.azimuth_degree)),
        #                                                               str(np.amax(self.azimuth_degree)),
        #                                                               str(np.std(self.azimuth_degree)) ))
        # cv2.imwrite('../tests/testData/LiveProcessed/I_trans.tif', self.I_trans)
        # cv2.imwrite('../tests/testData/LiveProcessed/retard.tif', self.retard)
        # cv2.imwrite('../tests/testData/LiveProcessed/scattering.tif', self.scattering)
        # cv2.imwrite('../tests/testData/LiveProcessed/azimuth_degree.tif', self.azimuth_degree)

        return True

    def imBitConvert(self, im, bit=16, norm=False, limit=None):
        # print('\t bit conversion')
        im = im.astype(np.float32, copy=False)  # convert to float32 without making a copy to save memory
        if norm:  # local or global normalization (for tiling)
            if not limit:  # if lmit is not provided, perform local normalization, otherwise global (for tiling)
                limit = [np.nanmin(im[:]), np.nanmax(im[:])]  # scale each image individually based on its min and max
            im = (im - limit[0]) / (limit[1] - limit[0]) * (2 ** bit - 1)
        else:  # only clipping, no scaling
            im = np.clip(im, 0, 2 ** bit - 1)  # clip the values to avoid wrap-around by np.astype
        if bit == 8:
            im = im.astype(np.uint8, copy=False)  # convert to 8 bit
        else:
            im = im.astype(np.uint16, copy=False)  # convert to 16 bit
        return im

    '''
    #===============================================================================
    #=========  some extra stuff ===================================================
    #===============================================================================
    Key notes:
        1) I change all functions to set class properties instead of passing image data
    '''

    def bitconvert(self, im):
        max = np.max(im)
        min = np.min(im)
        im = (2**16) * (im - min) / (max - min)
        return im.astype(np.float32, copy=False)

    def scale_all(self):
        self.azimuth_degree = self.bitconvert(self.azimuth_degree)
        self.scattering = self.bitconvert(self.scattering)
        self.retard = self.bitconvert(self.retard)
        self.I_trans = self.bitconvert(self.I_trans)
