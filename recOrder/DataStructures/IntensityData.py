import numpy as np

#todo: generalize variable names to be not strictly I0, I45 etc.?


class IntensityData(object):
    """
    Data Structure that contains all raw intensity images used for computing Stokes matrices
    only attributes with getters/setters can be assigned to this class
    """

    __IExt = None
    __I0 = None
    __I45 = None
    __I90 = None
    __I135 = None
    __data = None
    __frames = None

    def __setattr__(self, name, value):
        """
        Prevent attribute assignment other than those defined below
        :param name: any attribute
        :param value: corresponding value
        :return:
        """
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set name %r on object of type %s' % (
                name, self.__class__.__name__))

    def __init__(self, frames: int = 5):
        """
        Initialize instance variables
        :param frames: default is 5
        """
        super(IntensityData, self).__init__()
        self.__IExt = None
        self.__I0 = None
        self.__I45 = None
        self.__I90 = None
        self.__I135 = None
        self.__data = [None for _ in range(frames)]
        self.__frames = frames

    def check_shape(self):
        """
        check for None type or for inconsistency
        :return: boolean
        """
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
        """
        No setter for this, as it should be built by assigning components
        :return:
        """
        if not self.check_shape():
            raise ValueError("Inconsistent data dimensions or data not assigned\n")
        return np.array(self.__data)

    @property
    def frames(self):
        """
        no setter for this, which should be assigned at construction
        :return:
        """
        return self.__frames

    @property
    def IExt(self):
        return self.__IExt

    @IExt.setter
    def IExt(self, image: np.ndarray):
        self.__data[0] = image
        self.__IExt = image

    @property
    def I0(self):
        return self.__I0

    @I0.setter
    def I0(self, image: np.ndarray):
        self.__data[1] = image
        self.__I0 = image

    @property
    def I45(self):
        return self.__I45

    @I45.setter
    def I45(self, image: np.ndarray):
        self.__data[2] = image
        self.__I45 = image

    @property
    def I90(self):
        return self.__I90

    @I90.setter
    def I90(self, image: np.ndarray):
        self.__data[3] = image
        self.__I90 = image

    @property
    def I135(self):
        return self.__I135

    @I135.setter
    def I135(self, image: np.ndarray):
        self.__data[4] = image
        self.__I135 = image