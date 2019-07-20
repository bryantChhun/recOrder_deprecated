import numpy as np
from ReconstructOrder.datastructures.IntensityData import IntensityData


class StokesData(object):
    """
    Data Structure that contains all stokes images
    only attributes with getters/setters can be assigned to this class
    """

    __s0 = None
    __s1 = None
    __s2 = None
    __s3 = None
    __s1_norm = None
    __s2_norm = None
    __data = None

    def __setattr__(self, name, value):
        """
        Prevent attribute assignment other than those defined below
        :param name: str
            attribute name
        :param value: value
            attribute value
        :return:
        """
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set name %r on object of type %s' % (
                name, self.__class__.__name__))

    def __init__(self, inv_inst_matrix=None, intensity_data=None):
        """
        Initialize instance variables
        :param inv_inst_matrix: np.array
            inverse instrument matrix
            if provided with intensity data, automatically compute stokes matrices
        :param intensity_data: np.array
            if provided with inv_inst_matrix, automatically compute stokes matrices
        """
        super(StokesData, self).__init__()
        if inv_inst_matrix is not None and intensity_data is not None:
            self.__data = [None, None, None, None]
            self.compute_stokes(inv_inst_matrix, intensity_data)
        else:
            self.__s0 = None
            self.__s1 = None
            self.__s2 = None
            self.__s3 = None
            self.__s1_norm = None
            self.__s2_norm = None
            self.__data = [None, None, None, None]

    def compute_stokes(self, inv_inst_matrix, intensity_data: IntensityData):
        """
        compute and assign stokes matrices based on supplied inst matrix and intensity data
        :param inv_inst_matrix: inverse of instrument matrix
        :param intensity_data: IntensityData datastructure
        :return:
        """
        img_shape = np.shape(intensity_data.data)
        img_raw_flat = np.reshape(intensity_data.data, (intensity_data.frames, -1))
        img_stokes_flat = np.dot(inv_inst_matrix, img_raw_flat)
        img_stokes = np.reshape(img_stokes_flat, (4,) + img_shape[1:])
        [self.s0, self.s1, self.s2, self.s3] = [img_stokes[i, ...] for i in range(4)]
        self.s1_norm = self.s1/self.s3
        self.s2_norm = self.s2/self.s3

    def check_shape(self):
        current_shape = (0, 0)
        for img in np.array(self.__data):
            if img is None:
                return False
            elif current_shape == (0, 0):
                current_shape = img.shape
            elif img.shape != current_shape:
                return False
        return True

    @property
    def data(self):
        if not self.check_shape():
            raise ValueError("Inconsistent data dimensions or data not assigned\n")
        return np.array(self.__data)

    # Normalized S1 and S2
    @property
    def s1_norm(self):
        return self.__s1_norm

    @s1_norm.setter
    def s1_norm(self, image):
        self.__s1_norm = image

    @property
    def s2_norm(self):
        return self.__s2_norm

    @s2_norm.setter
    def s2_norm(self, image):
        self.__s2_norm = image

    # Stokes matrices
    @property
    def s0(self):
        return self.__s0

    @s0.setter
    def s0(self, image: np.ndarray):
        self.__s0 = image
        self.__data[0] = image

    @property
    def s1(self):
        return self.__s1

    @s1.setter
    def s1(self, image: np.ndarray):
        self.__s1 = image
        self.__data[1] = image

    @property
    def s2(self):
        return self.__s2

    @s2.setter
    def s2(self, image: np.ndarray):
        self.__s2 = image
        self.__data[2] = image

    @property
    def s3(self):
        return self.__s3

    @s3.setter
    def s3(self, image: np.ndarray):
        self.__s3 = image
        self.__data[3] = image


