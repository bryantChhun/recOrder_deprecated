

import numpy as np

from recOrder.datastructures import IntensityData
from recOrder.datastructures import PhysicalData
from recOrder.datastructures import StokesData
from recOrder.datastructures import BackgroundData

# from recOrder.analysis.Processing.VectorLayerUtils import convert_to_vector
from recOrder.analysis._analyze_base import AnalyzeBase
from recOrder.analysis.Quiver import build_quiver_image
from recOrder.analysis.PolColor import color_wheel

from typing import Union
from PyQt5.QtCore import QRunnable, QThreadPool


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        super().__init__()
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class ReconOrder(AnalyzeBase):
    """
    wrapper for the ImgReconstructor class from ReconstructOrder
    """

    inst_mat_inv = None
    transmission_scale = None
    retardance_scale = None
    orientation_scale = None
    polarization_scale = None
    black_level = None

    # background data if using bg correction
    background = None

    def __init__(self,
                 frames,
                 swing,
                 stokes_receiver_channel=11, stokes_emitter_channel=12,
                 physical_receiver_channel=12, physical_emitter_channel=1):

        super().__init__()

        self.Reconstructor = None

        self._frames = frames

        self.height = None
        self.width = None
        self.depth = None

        self._swing = swing
        self._swing_rad = self._swing*2*np.pi # covert swing from fraction of wavelength to radian
        self.wavelength = 532

        self.flip_pol = None
        self.local_gauss = None

        self.compute_inst_matrix()

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

    def compute_inst_matrix(self):
        """
        this is done in ReconstructOrder's initializer
        """
        if self.depth:
            self.Reconstructor = ImgReconstructor(img_shape=(self._frames, self.height, self.width, self.depth),
                                                  swing=self._swing,
                                                  wavelength=self.wavelength)
        else:
            self.Reconstructor = ImgReconstructor(img_shape=(self._frames, self.height, self.width),
                                                  swing=self._swing,
                                                  wavelength=self.wavelength)

    @AnalyzeBase.receiver(channel=11)
    def start_recon(self, int_obj):
        """
        Kick off a process for reconstruction to prevent GUI locking
        :param int_obj: IntensityData
            received from ReconOrderMonitor
        :return:
        """
        p = ProcessRunnable(target=self.recon_from_monitor, args=(int_obj,))
        p.start()

    @AnalyzeBase.emitter(channel=1)
    def recon_from_monitor(self, int_obj: IntensityData):
        """
        Sequence of analysis to build birefring. data
        Calls wrapper functions only
        :param int_obj: IntensityData
        :return: phys: PhysicalData
        """
        stk = self.compute_stokes(int_obj)
        stk_norm = self.stokes_normalization(stk)

        if self.background:
            print('pre-defined background found, correcting and computing')
            corrected = self.correct_background(stk_norm, self.background)
            phys = self.compute_physical(corrected)
        else:
            print('background NOT found, constructing dummy normalization')
            phys = self.compute_physical(stk_norm)

        self.start_colorwheel(phys.retard, phys.azimuth)
        phys = self.rescale_bitdepth(phys)

        return phys

    def compute_stokes(self, int_obj: IntensityData) -> StokesData:
        return self.Reconstructor.compute_stokes(int_obj)

    def stokes_normalization(self, stokes_param: Union[StokesData, BackgroundData]) -> BackgroundData:
        return self.Reconstructor.stokes_normalization(stokes_param)

    def correct_background(self, sample_data: BackgroundData, background_data: BackgroundData) -> BackgroundData:
        return self.Reconstructor.correct_background(sample_data, background_data)

    def compute_physical(self, data: Union[StokesData, BackgroundData], flip_pol='rcp') -> PhysicalData:

        if isinstance(data, BackgroundData):
            print('computing physical with background data')
            """
            data is normalized
            """
            output_physical = self.Reconstructor.reconstruct_birefringence(data)
        elif isinstance(data, StokesData):
            print('no background found: computing dummy normalization')
            """
            Data is not normalized, not background corrected
            will construct a dummy normalization
            """
            stokes_normalized = BackgroundData()
            stokes_normalized.s0 = data.s0
            stokes_normalized.s1 = data.s1
            stokes_normalized.s2 = data.s2
            stokes_normalized.s3 = data.s3
            stokes_normalized.s1_norm = data.s1 / data.s3
            stokes_normalized.s2_norm = data.s2 / data.s3
            stokes_normalized.polarization = np.sqrt(data.s1 ** 2 + data.s2 ** 2 + data.s3 ** 2) / data.s0
            # stokes_normalized.depolarization = 1 - stokes_normalized.polarization

            output_physical = self.Reconstructor.reconstruct_birefringence(stokes_normalized)
        else:
            raise TypeError("compute physical requires data of type StokesData or BackgroundData")

        # output_physical = self.rescale_bitdepth(output_physical)

        # append coordinate data for napari

        return output_physical

    def rescale_bitdepth(self, phy_obj: PhysicalData):

        phy_obj.retard = phy_obj.retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]

        # AU, set norm to False for tiling images
        phy_obj.I_trans = self.imBitConvert(phy_obj.I_trans * self.transmission_scale, bit=16, norm=True)
        phy_obj.retard = self.imBitConvert(phy_obj.retard * self.retardance_scale, bit=16)  # scale to pm
        phy_obj.polarization = self.imBitConvert(phy_obj.polarization * self.polarization_scale, bit=16)
        # phy_obj.depolarization = self.imBitConvert(phy_obj.depolarization * self.polarization_scale, bit=16)
        # scale to [0, 18000], 100*degree
        phy_obj.azimuth_degree = self.imBitConvert(phy_obj.azimuth_degree * self.orientation_scale, bit=16)
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

    # def start_orientation(self, image, orientation):
    #     p = ProcessRunnable(target=self.compute_orientation, args=(image, orientation))
    #     p.start()
    #
    # @AnalyzeBase.emitter(channel=1)
    # def compute_orientation(self, image, orientation):
    #     # return tuple so napari gui recognizes a different type
    #     print("starting orientation render!")
    #     dat = build_quiver_image(image, orientation)
    #     return (dat, )

    def start_colorwheel(self, retardance, orientation):
        p = ProcessRunnable(target=self.compute_colorwheel, args=(retardance, orientation))
        p.start()

    @AnalyzeBase.emitter(channel=1)
    def compute_colorwheel(self, retardance, orientation):
        print("starting colorwheel calculation")
        cmap = color_wheel(retardance, orientation)
        return (cmap, )

# ===================================================================================================================


class ImgReconstructor:
    """
    ImgReconstructor contains methods to compute physical properties of birefringence
    given images collected with 4 or 5 polarization states

    Parameters
    ----------
    img_shape : tuple
        Shape of the input image (channel, y, x)
    bg_method : str
        "Global" or "Local". Type of background correction. "Global" will correct each image
         using the same background. "Local" will do correction with locally estimated
         background in addition to global background
    n_slice_local_bg : int
        Number of slices averaged for local background estimation
    swing : float
        swing of the elliptical polarization states in unit of fraction of wavelength
    wavelength : int
        wavelenhth of the illumination light (nm)
    kernel_size : int
        size of the Gaussian kernel for local background estimation
    poly_fit_order : int
        order of the polynomial used for 'Local_fit' background correction
    azimuth_offset : float
        offset of the orientation reference axis
    circularity : str
         ('lcp' or 'rcp') the circularity of the analyzer looking from the detector's point of view.
        Changing this flag will flip the slow axis horizontally.

    Attributes
    ----------
    img_shape : tuple
        Shape of the input image (channel, y, x)
    bg_method : str
        "Global" or "Local". Type of background correction. "Global" will correct each image
         using the same background. "Local" will do correction with locally estimated
         background in addition to global background
    n_slice_local_bg : int
        Number of slices averaged for local background estimation
    swing : float
        swing of the elliptical polarization states in unit of radian
    wavelength : int
        wavelenhth of the illumination light
    kernel_size : int
        size of the Gaussian kernel for local background estimation
    azimuth_offset : float
        offset of the orientation reference axis
    circularity : str
         ('lcp' or 'rcp') the circularity of the analyzer looking from the detector's point of view.
        Changing this flag will flip the slow axis horizontally.
    inst_mat_inv : 2d array
        inverse of the instrument matrix
    stokes_param_bg_tm :
        transformed global background Stokes parameters
    stokes_param_bg_local_tm :
        transformed local background Stokes parameters

    """

    def __init__(self,
                 img_shape=None,
                 bg_method='Global',
                 n_slice_local_bg=1,
                 swing=None,
                 wavelength=532,
                 kernel_size=401,
                 poly_fit_order=2,
                 azimuth_offset=0,
                 circularity='rcp',
                 binning=1):

        #todo: it is REQUIRED to define img_shape in init.  If you do not, then self._n_chann isn't set at init, which
        # means that the inst_matrix is not calculated.
        # setting img_shape property after init will NOT calculate inst_matrix
        # there is an assertion on img_shape property setter that requires you define img_shape.

        # image params
        self.img_shape = img_shape

        self.bg_method = bg_method
        self.n_slice_local_bg = n_slice_local_bg
        self.swing = swing * 2 * np.pi # covert swing from fraction of wavelength to radian
        self.wavelength = wavelength
        self.kernel_size = kernel_size
        self.poly_fit_order = poly_fit_order
        chi = self.swing
        if self._n_chann == 4:  # if the images were taken using 4-frame scheme
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        elif self._n_chann == 5:  # if the images were taken using 5-frame scheme
            inst_mat = np.array([[1, 0, 0, -1],
                                 [1, np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, np.sin(chi), -np.cos(chi)],
                                 [1, -np.sin(chi), 0, -np.cos(chi)],
                                 [1, 0, -np.sin(chi), -np.cos(chi)]])
        else:
            raise Exception('Expected image shape is (channel, y, x, z)...'
                            'The number of channels is {}, but allowed values are 4 or 5'.format(self._n_chann))

        self.inst_mat_inv = np.linalg.pinv(inst_mat)
        self.azimuth_offset = azimuth_offset/180*np.pi
        # self.stokes_param_bg_tm = []

        # self.stokes_param_bg_local_tm = []
        self.circularity = circularity
        self.binning = binning

    @property
    def img_shape(self):
        return self._img_shape

    @img_shape.setter
    def img_shape(self, shape):
        assert len(shape) == 3 or 4, \
            'ImgReconstructor only supports 2D image or 3D stack'
        self._img_shape = shape
        if len(shape) == 3:
            [self._n_chann, self._height, self._width] = shape
            self._depth = 1
        else:
            [self._n_chann, self._height, self._width, self._depth] = shape

    def compute_stokes(self, int_obj: IntensityData) -> StokesData:
        """
        Given raw polarization images, compute stokes images

        Parameters
        ----------
        int_obj : IntensityData
            input image with shape (channel, y, x) or (channel, z, y, x)

        Returns
        -------
        stokes parameters : list of nd array.
            [s0, s1, s2, s3]

        """
        if not isinstance(int_obj, IntensityData):
            raise TypeError("Incorrect Data Type: must be IntensityData")

        # commented out because mean_pooling_2d_stack isn't implemented in recOrder
        # handle mean_pooling np.array return
        # int_obj_array = mean_pooling_2d_stack(int_obj.data, self.binning)
        # for idx, image in enumerate(int_obj.data):
        #     int_obj.replace_image(int_obj_array[idx], idx)

        self.img_shape = np.shape(int_obj.data)

        if self._n_chann == 4:
            img_raw = np.stack((int_obj.get_image('IExt'),
                                int_obj.get_image('I45'),
                                int_obj.get_image('I90'),
                                int_obj.get_image('I135')))  # order the channel following stokes calculus convention
        elif self._n_chann == 5:
            img_raw = np.stack((int_obj.get_image('IExt'),
                                int_obj.get_image('I0'),
                                int_obj.get_image('I45'),
                                int_obj.get_image('I90'),
                                int_obj.get_image('I135')))  # order the channel following stokes calculus convention
        else:
            raise ValueError("Intensity data first dim must be # of channels.  Only n_chann = 4 or 5 implemented")

        # calculate stokes
        img_raw_flat = np.reshape(img_raw, (self._n_chann, -1))
        img_stokes_flat = np.dot(self.inst_mat_inv, img_raw_flat)
        img_stokes = np.reshape(img_stokes_flat, (4,) + self.img_shape[1:])

        out = StokesData()
        [out.s0,
         out.s1,
         out.s2,
         out.s3] = [img_stokes[i, :, :] for i in range(4)]

        return out

    def stokes_normalization(self, stokes_param: Union[StokesData, BackgroundData]) -> BackgroundData:
        """
        Computes S1 and S2 norms.  Computes normalized polarization.

        Parameters
        ----------
        stokes_param : Union[StokesData, BackgroundData]
            object of type StokesData or BackgroundData

        Returns
        -------
        BackgroundData :
            object of type BackgroundData

        """
        if not isinstance(stokes_param, StokesData) and not isinstance(stokes_param, BackgroundData):
            raise TypeError("stokes_param must be of type StokesData or BackgroundData")

        norm_dat = BackgroundData()

        [s0, s1, s2, s3] = stokes_param.data

        # set BackgroundData's normalized data
        norm_dat.s1_norm = s1 / s3
        norm_dat.s2_norm = s2 / s3
        norm_dat.I_trans = s0
        norm_dat.polarization = np.sqrt(s1 ** 2 + s2 ** 2 + s3 ** 2) / s0

        # set BackgroundData's stokes data
        [norm_dat.s0,
         norm_dat.s1,
         norm_dat.s2,
         norm_dat.s3] = stokes_param.data

        return norm_dat

    def correct_background_stokes(self, sample_norm_obj: BackgroundData, bg_norm_obj: BackgroundData) -> BackgroundData:
        """
        correct background of transformed Stokes parameters

        Parameters
        ----------
        sample_norm_obj : BackgroundData
            Object of type BackgroundData from normalized sample
        bg_norm_obj : BackgroundData
            Object of type BackgroundData from normalized background

        Returns
        -------
        BackgroundData
            Object of type BackgroundData with correction
        """
        # add a dummy z-dimension to background if sample image has xyz dimension
        if len(bg_norm_obj.s0.shape) < len(sample_norm_obj.s0.shape):
            # add blank axis to end of background images so it matches dim of input image
            bg_norm_obj.s0 = bg_norm_obj.s0[..., np.newaxis]
            bg_norm_obj.polarization = bg_norm_obj.polarization[..., np.newaxis]
            bg_norm_obj.s1_norm = bg_norm_obj.s1_norm[..., np.newaxis]
            bg_norm_obj.s2_norm = bg_norm_obj.s2_norm[..., np.newaxis]

        # perform the correction
        sample_norm_obj.s0 = sample_norm_obj.s0 / bg_norm_obj.s0
        sample_norm_obj.polarization = sample_norm_obj.polarization / bg_norm_obj.polarization
        sample_norm_obj.s1_norm = sample_norm_obj.s1_norm - bg_norm_obj.s1_norm
        sample_norm_obj.s2_norm = sample_norm_obj.s2_norm - bg_norm_obj.s2_norm

        return sample_norm_obj

    def correct_background(self, sample_data: BackgroundData, background_data: BackgroundData) -> BackgroundData:
        """
        Corrects background and (optionally) does local_fit or local_filter

        Parameters
        ----------
        sample_data : BackgroundData
            Object of type BackgroundData
        background_data : BackgroundData
            Object of type BackgroundData

        Returns
        -------
        BackgroundData
            Corrected data using local_fit, local_filter or global

        """

        if self.n_slice_local_bg > 1:
            assert len(np.shape(sample_data.data[0])) == 3, \
                'Input image has to have >1 z-slice for n_slice_local_bg > 1'

        # sample_stokes_norm_corrected has z-appended
        sample_stokes_norm_corrected = self.correct_background_stokes(sample_data, background_data)

        # if local BG correction
        if self.bg_method in ['Local_filter', 'Local_fit']:
            # average only along these 'correction' attributes
            correction = ['s0', 'polarization', 's1_norm', 's2_norm', 's3']

            sample_stokes_norm_local = BackgroundData()
            # if z-axis is present, average across all z for local BG correction
            ax = 2 if len(sample_stokes_norm_corrected.s0.shape) > 2 else None
            [sample_stokes_norm_local.s0,
             sample_stokes_norm_local.polarization,
             sample_stokes_norm_local.s1_norm,
             sample_stokes_norm_local.s2_norm,
             sample_stokes_norm_local.s3] = [np.mean(img, axis=ax) if ax else img for img in
                                       [sample_stokes_norm_corrected.__getattribute__(corr) for corr in correction]]

            local_background = self.compute_local_background(sample_stokes_norm_local)

            sample_stokes_norm_corrected = self.correct_background_stokes(sample_stokes_norm_corrected, local_background)

        return sample_stokes_norm_corrected

    def compute_local_background(self, stokes_param_sm_local_tm: BackgroundData) -> BackgroundData:
        """
        Estimate local Stokes background using Guassian filter
        Parameters
        ----------
        stokes_param_sm_local_tm : BackgroundData
            Transformed sample Stokes parameters

        Returns
        -------
        BackgroundData
            local background Stokes parameters
        """

        stokes_param_bg_local_tm = BackgroundData()

        print('Estimating local background...')
        if self.bg_method == 'Local_filter':
            estimate_bg = self._gaussian_blur
        elif self.bg_method == 'Local_fit':
            estimate_bg = self._fit_background
        else:
            raise ValueError('background method has to be "Local_filter" or "Local_fit"')

        # estimate bg only on these stokes datasets
        correction = ['s0', 'polarization', 's1_norm', 's2_norm', 's3']

        [stokes_param_bg_local_tm.s0,
         stokes_param_bg_local_tm.polarization,
         stokes_param_bg_local_tm.s1_norm,
         stokes_param_bg_local_tm.s2_norm,
         stokes_param_bg_local_tm.s3] = [estimate_bg(img) for img in
                                         [stokes_param_sm_local_tm.__getattribute__(corr) for corr in correction]]

        return stokes_param_bg_local_tm

    def _gaussian_blur(self, img):
        background = cv2.GaussianBlur(img, (self.kernel_size, self.kernel_size), 0)
        return background

    def _fit_background(self, img):
        bg_estimator = BackgroundEstimator2D()
        background = bg_estimator.get_background(img, order=self.poly_fit_order, normalize=False)
        return background

    def reconstruct_birefringence(self, stokes_param_sm_tm: BackgroundData,
                                  img_crop_ref=None, extra=False) -> PhysicalData:
        """compute physical properties of birefringence

        Parameters
        ----------
        stokes_param_sm_tm: list of nd array.
            Transformed sample Stokes parameters

        Returns
        -------
        list of nd array.
              Brightfield_computed, Retardance, Orientation, Polarization, 'Stokes_1', 'Stokes_2', 'Stokes_3'
        """
        # for low birefringence sample that requires 0 background, set extra=True to manually offset the background
        # Correction based on Eq. 16 in reference using linear approximation assuming small retardance for both sample and background

        # ASmBg = 0
        # s2_normSmBg = 0
        # if extra: # extra background correction to set backgorund = 0
        #     imList = [s1_normSm, s2_normSm]
        #     imListCrop = imcrop(imList, I_ext) # manually select ROI with only background retardance
        #     s1_normSmCrop,s2_normSmCrop = imListCrop
        #     s1_normSmBg = np.nanmean(s1_normSmCrop)
        #     s2_normSmBg = np.nanmean(s2_normSmCrop)

        phys_data = PhysicalData()

        s1 = stokes_param_sm_tm.s1_norm * stokes_param_sm_tm.s3
        s2 = stokes_param_sm_tm.s2_norm * stokes_param_sm_tm.s3
        retard = np.arctan2(np.sqrt(s1 ** 2 + s2 ** 2), stokes_param_sm_tm.s3)
        retard = retard / (2 * np.pi) * self.wavelength  # convert the unit to [nm]

        if self.circularity == 'lcp':
            azimuth = (0.5 * np.arctan2(s1, -s2) + self.azimuth_offset) % (np.pi)  # make azimuth fall in [0,pi]
        elif self.circularity == 'rcp':
            azimuth = (0.5 * np.arctan2(-s1, -s2) + self.azimuth_offset) % (np.pi)  # make azimuth fall in [0,pi]
        else:
            raise AttributeError("unable to compute azimuth, circularity parameter is not defined")

        phys_data.I_trans = stokes_param_sm_tm.s0
        phys_data.retard = retard
        phys_data.azimuth = azimuth
        phys_data.azimuth_degree = phys_data.azimuth / (np.pi) * 180
        phys_data.polarization = stokes_param_sm_tm.polarization
        phys_data.depolarization = stokes_param_sm_tm.depolarization

        return phys_data

    def calibrate_inst_mat(self):
        raise NotImplementedError
        pass


