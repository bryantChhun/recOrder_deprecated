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

    def __init__(self, num_channels=None, channel_names: list = None, axis_names: list = None):
        """
        Initialize instance variables
        :param channel_names:
        """
        super(IntensityData, self).__init__()
        self.__data = []
        self.__channel_names = channel_names
        self.__axis_names = axis_names

        if num_channels:
            for _ in range(num_channels):
                self.__data.append([])

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
            elif img == []:
                continue
            elif input_shape and input_shape != np.array(img).shape:
                return False
            elif current_shape == (0, 0):
                current_shape = np.array(img).shape
            elif np.array(img).shape != current_shape:
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
            raise TypeError("image is type %s.  Must be np.ndarray or np.memmap" % str(type(input())))
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

        # check that data contains entries for each of the channel names
        # if it does not, then add a blank entry
        if len(self.__data) <= len(self.__channel_names):
            for i in range(len(self.__channel_names)-len(self.__data)):
                self.__data.append([])

    @property
    def axis_names(self):
        return self.__channel_names

    @axis_names.setter
    def axis_names(self, value: list):
        """
        set names for axes
        :param value: list of str
        :return:
        """
        if len(set(value)) != len(value):
            raise ValueError("duplicate entries in axis_name list")
        else:
            self.__axis_names = value

    def append_image(self, image):
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
        try:
            self.check_dtype(image)
        except TypeError as te:
            print(te)

        # perform replacement THEN check for shape consistency
        if type(position) == int:
            if len(self.__data) <= position:
                raise IndexError("replacing Intensity Data image at position that does not exist")

            temp = self.get_image(position)
            self.__data[position] = image
            if not self.check_shape(image.shape):
                self.__data[position] = temp
                raise ValueError("image does not conform to current data dimensions")

        elif type(position) == str:
            if position not in self.__channel_names:
                raise IndexError("replacing Intensity Data image at channel name that is not defined")

            temp = self.get_image(position)
            self.__data[self.__channel_names.index(position)] = image
            if not self.check_shape(image.shape):
                self.__data[self.__channel_names.index(position)] = temp
                raise ValueError("image does not conform to current data dimensions")

    def get_image(self, position):
        """
        enable image search by channel name or index
        :param position: int or str
            if str, search for matching str in supplied channel_names
        :return:
        """
        if type(position) is str:
            if position in self.__channel_names:
                try:
                    dat = self.__data[self.__channel_names.index(position)]
                except TypeError:
                    raise TypeError("channel %s does not exist in data" % position)
                return dat
            else:
                raise ValueError("Intensity Data with channel name %s is not found")
        elif type(position) is int:
            return self.__data[position]
