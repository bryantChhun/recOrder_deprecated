import numpy as np


class IntensityData(object):
    """
    Data Structure that contains all raw intensity images used for computing Stokes matrices
    only attributes with getters/setters can be assigned to this class
    """

    __data = None
    __channel_names = None
    __axis_names = None

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

    def __init__(self, channel_names: list = None, axis_names: list = None):
        """
        Initialize instance variables
        :param channel_names:
        """
        super(IntensityData, self).__init__()
        self.__data = []
        self.__channel_names = channel_names
        self.__axis_names = axis_names

    def check_shape(self, input_shape=None):
        """
        check for None type or for inconsistency
        :return: boolean
        """
        current_shape = (0, 0)
        if len(self.__data) == 0:
            return True
        for img in self.__data:
            if img is None:
                return False
            elif input_shape and input_shape != img.shape:
                return False
            elif current_shape == (0, 0):
                current_shape = img.shape
            elif img.shape != current_shape:
                return False
        return True

    def check_dtype(self, input_data):
        """
        check that supplied images are either numpy arrays or memmaps
        :param input_data: np.ndarray, or np.memmap
        :return: boolean
        """
        if type(input_data) is not np.ndarray and \
                type(input_data) is not np.memmap:
            return False
        else:
            return True

    @property
    def data(self):
        """
        get the underlying np.array data that is built
        :return: np.array of data object
        """
        if not self.check_shape():
            raise ValueError("Inconsistent data dimensions or data not assigned\n")
        return np.array(self.__data)

    @property
    def num_channels(self):
        """
        Get the number of channels already assigned to the data
        :return: number of images assigned to this data
        """
        return len(self.__data)

    @property
    def channel_names(self):
        return self.__channel_names

    @channel_names.setter
    def channel_names(self, value: list):
        """
        set list of channel names
        :param value: list of str
        :return:
        """
        self.__channel_names = value

    @property
    def axis_names(self):
        return self.__channel_names

    @axis_names.setter
    def axis_names(self, value: list):
        """
        set names for axes (dimensionality)
        :param value: list of str
        :return:
        """
        if len(set(value)) != len(value):
            raise ValueError("duplicate entries in axis_name list")
        else:
            self.__axis_names = value

    def add_image(self, image):
        """
        append image to end of data
        :param image: np.ndarray or np.memmap
        :return:
        """
        if not self.check_dtype(image):
            raise TypeError("image is not ndarray")
        if not self.check_shape(image.shape):
            raise ValueError("image does not conform to current data dimensions")
        self.__data.append(image)

    def replace_image(self, image, position):
        if not self.check_dtype(image):
            raise TypeError("image is not ndarray")

        # perform replacement THEN check for shape consistency
        temp = self.get_image(position)
        self.__data[position] = image
        if not self.check_shape(image.shape):
            self.__data[position] = temp
            raise ValueError("image does not conform to current data dimensions")

    def get_image(self, param):
        """
        enable image search by channel name or index
        :param param: int or str
            if str, search for matching str in supplied channel_names
        :return:
        """
        if type(param) is str:
            if param in self.__channel_names:
                try:
                    dat = self.__data[self.__channel_names.index(param)]
                except TypeError:
                    raise TypeError("channel %s does not exist in data" % param)
                return dat
            else:
                raise ValueError("Intensity Data with channel name %s is not found")
        elif type(param) is int:
            return self.__data[param]
