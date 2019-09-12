

import numpy as np

from recOrder.datastructures import IntensityData
from recOrder.datastructures import PhysicalData
from recOrder.datastructures import StokesData
from recOrder.datastructures import BackgroundData

# from recOrder.analysis.Processing.VectorLayerUtils import convert_to_vector
from recOrder.analysis._analyze_base import AnalyzeBase


class ReconOrder(AnalyzeBase):
    """
    place analysis base emitters at each of the Intensity, Stokes and physical functions
    place analysis base slots at each of the intensity, Stokes and physical functions

    if it receives data from slot, it is called with inputs
    when it completes compute, it sends with emit
    """

    inst_mat_inv = None

    def __init__(self,
                 stokes_receiver_channel=11, stokes_emitter_channel=12,
                 physical_receiver_channel=12, physical_emitter_channel=13):
        super().__init__()

        self._frames = 5

        self.height = None
        self.width = None

        self._swing = 0.1
        self._swing_rad = self._swing*2*np.pi # covert swing from fraction of wavelength to radian
        self.wavelength = 532

        self.flip_pol = None

        self.local_gauss = None

        # decorations
        self.compute_stokes = \
            AnalyzeBase.bidirectional(emitter_channel=stokes_emitter_channel,
                                      receiver_channel=stokes_receiver_channel)(self.compute_stokes)
        self.compute_physical = \
            AnalyzeBase.bidirectional(emitter_channel=physical_emitter_channel,
                                      receiver_channel=physical_receiver_channel)(self.compute_physical)

        self.compute_inst_matrix()

    # ==== properties ====

    @property
    def frames(self) -> int:
        return self._frames

    @frames.setter
    def frames(self, num_frames):
        """
        set how many polarization intensity images are used for this reconstruction
        :param num_frames: integer 4 or 5
        :return:
        """
        if num_frames != 4 and num_frames != 5:
            raise NotImplementedError("support only 4 or 5 frame reconstructions")
        else:
            self._frames = num_frames

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

    # ==== compute functions ====

    def correct_background(self, stk_obj: StokesData, background: BackgroundData) -> PhysicalData:
        """
        Uses computed result from background images to calculate the correction
        :param stk_obj: StokesData
        :param background: ReconOrder object that is constructed from background images
        :return:
        """

        if isinstance(background, BackgroundData):
            stk_obj.s0 = stk_obj.s0 / background.s0
            stk_obj.s3 = stk_obj.s3 / background.s3
            stk_obj.s1_norm = stk_obj.s1_norm - background.s1_norm
            stk_obj.s2_norm = stk_obj.s2_norm - background.s2_norm

            new_phys = self.compute_physical(stk_obj)

            new_phys.polarization = new_phys.polarization / background.polarization

            return new_phys
        else:
            raise ModuleNotFoundError("background parameter must be a ReconOrder object")

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
            raise NotImplementedError('Frames not set to 4 or 5:  Required for calculation of instrument matrix')

        self.inst_mat_inv = np.linalg.pinv(inst_mat)

    def compute_stokes(self, int_obj: IntensityData) -> StokesData:
        """
        computes stokes vectors from the polarization intensities and instrument matrix

        :return: populated StokesData
        """
        print("computing stokes")

        output_stokes = StokesData()

        # define our instrument matrix based on self.frames
        if self._frames == 4:
            img_raw = np.stack((int_obj.get_image('IExt'),
                                int_obj.get_image('I45'),
                                int_obj.get_image('I90'),
                                int_obj.get_image('I135')))  # order the channel following stokes calculus convention
            n_chann = np.shape(img_raw)[0]
        elif self._frames == 5:
            img_raw = np.stack((int_obj.get_image('IExt'),
                                int_obj.get_image('I0'),
                                int_obj.get_image('I45'),
                                int_obj.get_image('I90'),
                                int_obj.get_image('I135')))  # order the channel following stokes calculus convention
            n_chann = np.shape(img_raw)[0]
        else:
            raise ValueError("frames must be 4 or 5 to perform stokes calculation")

        self.height = int_obj.get_image('IExt').shape[0]
        self.width = int_obj.get_image('IExt').shape[1]

        # calculate stokes
        img_raw_flat = np.reshape(img_raw,(n_chann, self.height*self.width))
        img_stokes_flat = np.dot(self.inst_mat_inv, img_raw_flat)
        img_stokes = np.reshape(img_stokes_flat, (img_stokes_flat.shape[0], self.height, self.width))

        [output_stokes.s0,
         output_stokes.s1,
         output_stokes.s2,
         output_stokes.s3] = [img_stokes[i, :, :] for i in range(0, img_stokes.shape[0])]

        return output_stokes

    def compute_physical(self, stk_obj: StokesData, flip_pol='rcp') -> PhysicalData:
        """
        computes physical results from the stokes vectors
            transmittance
            retardance
            polarization
            depolarization
            azimuth
            azimuth_vector
        :param stk_obj: object of type StokesData
        :param flip_pol: whether azimuth is flipped based on rcp/lcp analyzer
        :return: PhysicalData object
        """
        print("computing physical")

        output_physical = PhysicalData()

        s0 = stk_obj.s0
        s1 = stk_obj.s1
        s2 = stk_obj.s2
        s3 = stk_obj.s3

        output_physical.I_trans = s0
        output_physical.retard = np.arctan2(np.sqrt(s1 ** 2 + s2 ** 2), s3)
        output_physical.polarization = np.sqrt(s1 ** 2 + s2 ** 2 + s3 ** 2) / s0
        output_physical.depolarization = 1 - output_physical.polarization

        if flip_pol == 'rcp':
            self.flip_pol = flip_pol
            output_physical.azimuth = (0.5 * np.arctan2(-s1, s2) % np.pi)  # make azimuth fall in [0,pi]
        else:
            self.flip_pol = 'lcp'
            output_physical.azimuth = (0.5 * np.arctan2(s1, s2) % np.pi)  # make azimuth fall in [0,pi]

        output_physical.azimuth_degree = output_physical.azimuth / (np.pi) * 180
        # output_physical.azimuth_vector = convert_to_vector(output_physical.azimuth,
        #                                                    output_physical.retard)

        output_physical = self.rescale_bitdepth(output_physical)

        return output_physical

    # ==== data scaling ====

    def rescale_bitdepth(self, phy_obj: PhysicalData):

        phy_obj.retard = phy_obj.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]

        # AU, set norm to False for tiling images
        phy_obj.I_trans = self.imBitConvert(phy_obj.I_trans * 10 ** 4, bit=16, norm=True)
        phy_obj.retard = self.imBitConvert(phy_obj.retard * 10 ** 4, bit=16)  # scale to pm
        phy_obj.depolarization = self.imBitConvert(phy_obj.depolarization * 10 ** 5.5, bit=16)
        # scale to [0, 18000], 100*degree
        phy_obj.azimuth_degree = self.imBitConvert(phy_obj.azimuth_degree * 100, bit=16)
        return phy_obj

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

    def stretch_scale(self, phy_obj: PhysicalData):
        phy_obj.retard = phy_obj.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]

        phy_obj.I_trans = self.stretch_convert(phy_obj.I_trans)
        phy_obj.retard = self.stretch_convert(phy_obj.retard)
        phy_obj.depolarization = self.stretch_convert(phy_obj.depolarization)
        phy_obj.azimuth_degree = self.stretch_convert(phy_obj.azimuth_degree)

        return phy_obj

    def stretch_convert(self, im):
        im = im.astype(np.float32, copy=False)
        im = (im - np.min(im)) / (np.max(im) - np.min(im))
        return im