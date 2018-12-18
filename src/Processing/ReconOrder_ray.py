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
import ray

from src.Processing.ReconExceptions import InsufficientDataError, InvalidFrameNumberDeclarationError, InvalidBackgroundObject

from datetime import datetime

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
    4) Call compute Jones/Stokes
    5) Call reconstruct_img
'''

@ray.remote
class ReconOrder_ray(object):

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

        #make results a class property.  This is so PyQT elements can retrieve it without sockets
        self.I_trans = None
        self.polarization = None
        self.A = None
        self.B = None
        self.dAB = None

        self.retard = None
        self.azimuth = None
        self.scattering = None
        self.azimuth_degree = None

        self.local_gauss = None

    def set_frames(self, num_frames = 4):
        if num_frames != 4 and num_frames != 5:
            raise InvalidFrameNumberDeclarationError("support only 4 or 5 frame reconstructions")
        else:
            self._frames = num_frames
        return True

    def get_frames(self) -> int:
        return self._frames

    def set_state(self, state: int, img: np.array):
        """
        Assigns an image to a list of states.  Each image corresponds to one of required polarizations
        :param state: list index used for assignment
        :param img: 2d numpy array.
        :return: None
        """
        self._states[state] = img
        self.height = self._states[state].shape[0]
        self.width = self._states[state].shape[1]

    def get_state(self, state: int) -> np.array:
        return self._states[state]

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

    def correct_background_localGauss(self):
        self.local_gauss = ReconOrder()

        self.local_gauss.I_trans = cv2.GaussianBlur(self.I_trans, (401, 401), 0)
        self.local_gauss.polarization = cv2.GaussianBlur(self.polarization, (401, 401), 0)
        self.local_gauss.A = cv2.GaussianBlur(self.A, (401, 401), 0)
        self.local_gauss.B = cv2.GaussianBlur(self.B, (401, 401), 0)
        self.local_gauss.dAB = cv2.GaussianBlur(self.dAB, (401, 401), 0)
        self.correct_background(self.local_gauss)
        return True

    '''
    #===============================================================================
    #=========  Everything below is taken from Syuan-Ming's reconOrder code ========
    #===============================================================================
    Key notes:
        1) I change all functions to set class properties instead of passing image data
    '''

    def compute_jones(self) -> bool:
        if self._frames is None:
            raise InvalidFrameNumberDeclarationError("Number of frames not defined")
        for idx, element in enumerate(self._states[:-1]):
            if element is None:
                raise InsufficientDataError("No image loaded for index = %01d" % idx)

        chi = self.swing
        I_ext = self._states[0] # Sigma0 in Fig.2
        I_90 = self._states[1] # Sigma2 in Fig.2
        I_135 = self._states[2] # Sigma4 in Fig.2
        I_45 = self._states[3] # Sigma3 in Fig.2
        polarization = np.ones((self.height, self.width))  # polorization is always 1 for Jones calculus
        if self._frames == 4:  # 4-frame algorithm
            nB = (I_135 - I_45) * np.tan(chi / 2)
            nA = (I_45 + I_135 - 2 * I_90) * np.tan(chi / 2)  # Eq. 10 in reference
            dAB = I_45 + I_135 - 2 * I_ext
            A = nA / dAB
            B = nB / dAB
            I_trans = I_45 + I_135 - 2 * np.cos(chi) * I_ext
        elif self._frames == 5:  # 5-frame algorithm
            if self._states[4] is None:
                raise InsufficientDataError("No image loaded for index = 4")
            I_0 = self._states[4]  # Sigma1 in Fig.2
            nB = (I_135 - I_45) * np.tan(chi / 2)
            dB = I_135 + I_45 - 2 * I_ext
            nA = (I_0 - I_90) * np.tan(chi / 2)
            dA = I_0 + I_90 - 2 * I_ext  # Eq. 10 in reference
            dB[dB == 0] = np.spacing(1.0)
            dA[dA == 0] = np.spacing(1.0)
            A = nA / dA
            B = nB / dB
            I_trans = I_45 + I_135 - 2 * np.cos(chi) * I_ext
            dAB = (dA + dB) / 2

        self.I_trans = I_trans
        self.polarization = polarization
        self.A = A
        self.B = B
        self.dAB = dAB

        return True

    # @ray.remote
    def compute_stokes(self) -> bool:
        if self._frames is None:
            raise InvalidFrameNumberDeclarationError("Number of frames not defined")
        for idx, element in enumerate(self._states[:-1]):
            if element is None:
                raise InsufficientDataError("No image loaded for index = %01d" % idx)

        chi = self.swing
        I_ext = self._states[0] # Sigma0 in Fig.2
        I_90 = self._states[1] # Sigma2 in Fig.2
        I_135 = self._states[2] # Sigma4 in Fig.2
        I_45 = self._states[3] # Sigma3 in Fig.2
        # polarization = np.ones((self.height, self.width))  # polorization is always 1 for Jones calculus
        if self._frames == 4:  # if the images were taken using 4-frame scheme
            img_raw = np.stack((I_ext, I_45, I_90, I_135))  # order the channel following stokes calculus convention
            # n_chann is always 4 here
            self.n_chann = np.shape(img_raw)[0]
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        elif self._frames == 5:  # if the images were taken using 5-frame scheme
            if self._states[4] is None:
                raise InsufficientDataError("No image loaded for index = 4")

            I_0 = self._states[4]
            img_raw = np.stack((I_ext, I_0, I_45, I_90, I_135))  # order the channel following stokes calculus convention
            # n_chann is always 5 here
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
        [s0, s1, s2, s3] = [img_stokes[i, :, :] for i in range(0, img_stokes.shape[0])]
        A = s1/s3
        B = -s2/s3
        I_trans = s0
        polarization = np.sqrt(s1 ** 2 + s2 ** 2 + s3 ** 2)/s0
        dAB = s3

        self.I_trans = I_trans
        self.polarization = polarization
        self.A = A
        self.B = B
        self.dAB = dAB

        return True

    # def correct_background(self, img_param_sm: list, img_param_bg: list) -> (np.array, np.array, np.array, np.array, np.array):
    #
    #     [I_trans_sm, polarization_sm, A_sm, B_sm, dAB_sm] = img_param_sm
    #     [I_trans_bg, polarization_bg, A_bg, B_bg, dAB_bg] = img_param_bg
    #     I_trans_sm = I_trans_sm/I_trans_bg
    #     polarization_sm = polarization_sm/polarization_bg
    #     A_sm = A_sm - A_bg
    #     B_sm = B_sm - B_bg
    #
    #     return I_trans_sm, polarization_sm, A_sm, B_sm, dAB_sm

    def reconstruct_img(self, flipPol=False):
        # if self.method == 'Jones':
        # [I_trans, polarization, A, B, dAB] = img_param

        A = self.A
        B = self.B
        dAB = self.dAB

        self.retard = np.arctan(np.sqrt(A ** 2 + B ** 2))
        retardNeg = np.pi + np.arctan(
            np.sqrt(A ** 2 + B ** 2))  # different from Eq. 10 due to the definition of arctan in numpy
        DeltaMask = dAB >= 0  # Mask term in Eq. 11
        self.retard[~DeltaMask] = retardNeg[~DeltaMask]  # Eq. 11
        self.retard = self.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]

        if flipPol:
            self.azimuth = (0.5 * np.arctan2(-A, B) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
        else:
            self.azimuth = (0.5 * np.arctan2(A, B) + 0.5 * np.pi)  # make azimuth fall in [0,pi]

        # elif self.method == 'Stokes':
        #     [s0, s1, s2, s3] = img_param
        #     retard = np.arctan2(s3, np.sqrt(s1 ** 2 + s2 ** 2))
        #     retard = (retard + np.pi) % np.pi
        #     if flipPol:
        #         # azimuth = (0.5 * np.arctan2(-s1, s2) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
        #         azimuth = 0.5 * ((np.arctan2(-s1, s2) + 2 * np.pi) % (2 * np.pi))
        #     else:
        #         azimuth = (0.5 * np.arctan2(s1, s2) + 0.5 * np.pi)  # make azimuth fall in [0,pi]
        #     polarization = np.sqrt(s1 ** 2 + s2 ** 2 + s3 ** 2)/s0

        self.rescale_bitdepth()

        # cv2.imwrite('/Volumes//RAM_disk/I_trans.tif', self.I_trans)
        # cv2.imwrite('/Volumes//RAM_disk/retard.tif', self.retard)
        # cv2.imwrite('/Volumes//RAM_disk/scattering.tif', self.scattering)
        # cv2.imwrite('/Volumes//RAM_disk/azimuth_degree.tif', self.azimuth_degree)

        return True

    def rescale_bitdepth(self):
        start = datetime.now()
        self.scattering = 1 - self.polarization
        self.azimuth_degree = self.azimuth/np.pi*180
        # print(str(self.I_trans.dtype)+" "+str(np.max(self.I_trans)))
        # print(str(self.retard.dtype)+" "+str(np.max(self.retard)))
        # print(str(self.scattering.dtype)+" "+str(np.max(self.scattering)))
        # print(str(self.azimuth_degree.dtype)+" "+str(np.max(self.azimuth_degree)))

        self.I_trans = self.imBitConvert(self.I_trans * 10 ** 3, bit=16, norm=True)  # AU, set norm to False for tiling images
        self.retard = self.imBitConvert(self.retard * 10 ** 3, bit=16)  # scale to pm
        self.scattering = self.imBitConvert(self.scattering * 10 ** 4, bit=16)
        self.azimuth_degree = self.imBitConvert(self.azimuth_degree * 100, bit=16)  # scale to [0, 18000], 100*degree

        stop = datetime.now()
        print("\trescale bitdepth = "+str((stop-start).microseconds))

        return True

    def imBitConvert(self, im, bit=16, norm=False, limit=None):
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
