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

from src.DataStructures.IntensityData import IntensityData
from src.DataStructures.PhysicalData import PhysicalData
from src.DataStructures.StokesData import StokesData
from src.DataStructures.BackgroundData import BackgroundData
from src.Processing.AzimuthToVector import compute_average


'''
ReconOrder contains all methods to reconstruct polarization images (transmittance, retardance, orientation, scattering)
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

    inst_mat_inv = None

    def __init__(self):
        super(ReconOrder, self).__init__()
        self._intensity = IntensityData()
        self._states = [None] * 5
        self._frames = None

        self.height = None
        self.width = None

        self._swing = 0.1
        self._swing_rad = self._swing*2*np.pi # covert swing from fraction of wavelength to radian
        self.wavelength = 532

        self.flip_pol = None

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

        # physical images
        self.retard = None
        self.azimuth = None
        self.scattering = None
        self.azimuth_degree = None

        self.azimuth_vector = None

        self.local_gauss = None

    @property
    def IntensityData(self):
        return self._intensity

    @IntensityData.setter
    def IntensityData(self, int_obj: IntensityData):
        self._intensity = int_obj
        self.state = (0, int_obj.Iext)
        self.state = (1, int_obj.Iext)
        self.state = (2, int_obj.Iext)
        self.state = (3, int_obj.Iext)
        self.state = (4, int_obj.Iext)

    @property
    def frames(self) -> int:
        return self._frames

    @frames.setter
    def frames(self, num_frames=4):
        """
        set how many polarization intensity images are used for this reconstruction
        :param num_frames: integer 4 or 5
        :return:
        """
        if num_frames != 4 and num_frames != 5:
            raise InvalidFrameNumberDeclarationError("support only 4 or 5 frame reconstructions")
        else:
            self._frames = num_frames

    @property
    def state(self) -> np.array:
        return self._states

    @state.setter
    def state(self, statemap: tuple):
        """
        Assigns an image to a list of states.  Each image corresponds to one of required polarizations
        :param statemap: tuple of (state index, np.array)
        :return: none
        """
        if len(statemap) != 2:
            raise ValueError("invalid state parameter: state setter receives tuple of (index, image)")
        self._states[statemap[0]] = statemap[1]
        self._intensity.set_angle_from_index(statemap[0], statemap[1])

        self.height = self._states[statemap[0]].shape[0]
        self.width = self._states[statemap[0]].shape[1]

    @property
    def swing(self):
        return self._swing

    @swing.setter
    def swing(self, x: float):
        """
        The swing used during LC calibration for this dataset
        :param x: float value should be fraction of wavelength
        :return:
        """
        if x < -1 or x > 1:
            raise ValueError("swing of %f is too low or high.  Should be fraction of wavelength between -1 and 1" % x)
        self._swing = x
        self._swing_rad = self._swing*2*np.pi

    def correct_background(self, background: object):
        """
        Uses computed result from background images to calculate the correction
        :param background: ReconOrder object that is constructed from background images
        :return: None
        """

        if isinstance(background, ReconOrder) or isinstance(background, BackgroundData):
            self.I_trans = self.I_trans / background.I_trans
            self.polarization = self.polarization / background.polarization
            self.A = self.A - background.A
            self.B = self.B - background.B
            return True
        else:
            raise InvalidBackgroundObject("background parameter must be a ReconOrder object or None (for local Gauss)")

    def compute_inst_matrix(self):
        chi = self._swing_rad
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
        return None

    def compute_stokes(self):
        """
        computes stokes vectors from the polarization intensities and instrument matrix

        :return:
        """
        chi = self._swing_rad
        I_ext = self.state[0]
        I_90 = self.state[1]
        I_135 = self.state[2]
        I_45 = self.state[3]

        # define our instrument matrix based on self.frames
        if self._frames == 4:
            img_raw = np.stack((I_ext, I_45, I_90, I_135))  # order the channel following stokes calculus convention
            self.n_chann = np.shape(img_raw)[0]
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        elif self._frames == 5:
            I_0 = self.state[4]
            img_raw = np.stack((I_ext, I_0, I_45, I_90, I_135))  # order the channel following stokes calculus convention
            self.n_chann = np.shape(img_raw)[0]
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])

        # calculate stokes
        inst_mat_inv = np.linalg.pinv(inst_mat)
        img_raw_flat = np.reshape(img_raw,(self.n_chann, self.height*self.width))
        img_stokes_flat = np.dot(inst_mat_inv, img_raw_flat)
        img_stokes = np.reshape(img_stokes_flat, (img_stokes_flat.shape[0], self.height, self.width))
        [self.s0, self.s1, self.s2, self.s3] = [img_stokes[i, :, :] for i in range(0, img_stokes.shape[0])]

        # assign normalized vectors for bg correction
        self.A = self.s1 / self.s3
        self.B = -self.s2 / self.s3

    def compute_physical(self, flip_pol='rcp', avg_kernel=(1, 1)):
        '''
        computes physical results from the stokes vectors
            transmittance
            retardance
            polarization
            scattering
            azimuth
            azimuth_vector
        :param flip_pol:
        :param avg_kernel: kernel over which to average azimuth
        :return:
        '''

        # compute s1 and s2 from background corrected A and B
        s1 = self.A * self.s3
        s2 = -self.B * self.s3

        self.I_trans = self.s0
        self.retard = np.arctan2(np.sqrt(s1 ** 2 + s2 ** 2), self.s3)
        self.polarization = np.sqrt(s1 ** 2 + s2 ** 2 + self.s3 ** 2) / self.s0
        self.scattering = 1 - self.polarization

        if flip_pol == 'rcp':
            self.flip_pol = flip_pol
            self.azimuth = (0.5 * np.arctan2(-s1, s2) % np.pi)  # make azimuth fall in [0,pi]
        else:
            self.flip_pol = 'lcp'
            self.azimuth = (0.5 * np.arctan2(s1, s2) % np.pi)  # make azimuth fall in [0,pi]

        #make the arrays displayable by scaling to more meaningful values
        # self.retard = self.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]
        # self.azimuth_degree = self.azimuth/np.pi*180
        # self.azimuth_vector = convert_to_vector(self.azimuth - (0.5*np.pi))
        _, _, self.azimuth_vector = compute_average(s1, s2, self.s3, kernel=avg_kernel, length=5, flipPol=flip_pol)

        return True

    def rescale_bitdepth(self):
        self.retard = self.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]
        self.azimuth_degree = self.azimuth/np.pi*180

        self.I_trans = self.imBitConvert(self.I_trans * 10 ** 3, bit=16, norm=True)  # AU, set norm to False for tiling images
        self.retard = self.imBitConvert(self.retard * 10 ** 3, bit=16)  # scale to pm
        self.scattering = self.imBitConvert(self.scattering * 10 ** 4, bit=16)
        self.azimuth_degree = self.imBitConvert(self.azimuth_degree * 100, bit=16)  # scale to [0, 18000], 100*degree

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


class InsufficientDataError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class InvalidFrameNumberDeclarationError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class InvalidBackgroundObject(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message