
from .IntensityData import IntensityData
from .StokesData import StokesData
from .PhysicalData import PhysicalData


class Singleton(type):
    """
    metaclass that guarantees that exactly one instance of subclass exists
    set metaclass = Singleton if you want a Singleton design pattern
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BackgroundData(IntensityData, StokesData, PhysicalData):
    """
    by default, we will not make this a singleton
    """

    def __init__(self,
                 intensity_data = None,
                 stokes_data = None,
                 physical_data = None):
        super(BackgroundData, self).__init__()
        if intensity_data is not None:
            self.assign_intensity(intensity_data)
        if stokes_data is not None:
            self.assign_stokes(stokes_data)
        if physical_data is not None:
            self.assign_physical(physical_data)

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

    def assign_intensity(self, int_obj: IntensityData):
        for i in range(int_obj.num_channels):
            self.add_image(int_obj.get_image(i))

    def assign_stokes(self, stk_obj: StokesData):
        print("assigning stokes")
        print(type(stk_obj))
        self.s0 = stk_obj.s0
        self.s1 = stk_obj.s1
        self.s2 = stk_obj.s2
        self.s3 = stk_obj.s3

    def assign_physical(self, phy_obj: PhysicalData):
        self.I_trans = phy_obj.I_trans
        self.retard = phy_obj.retard
        self.polarization = phy_obj.polarization
        self.azimuth = phy_obj.azimuth
        self.azimuth_degree = phy_obj.azimuth_degree
        self.azimuth_vector = phy_obj.azimuth_vector
        self.depolarization = phy_obj.depolarization

    def print_none_vals(self):
        """
        prints to console all attributes that are NOT assigned

        :return:
        """
        intensity = ['IExt', 'I0', 'I45', 'I90', 'I135']
        stokes = ['s0', 's1', 's2', 's3', 's4']
        physical = ['I_trans', 'retard', 'polarization', 'azimuth', 'depolarization']
        for intensity_attribute in intensity:
            if getattr(self, intensity_attribute) is None:
                print("value not set = "+str(intensity_attribute))
        for stokes_attribute in stokes:
            if getattr(self, stokes_attribute) is None:
                print("value not set = "+str(stokes_attribute))
        for physical_attribute in physical:
            if getattr(self, physical_attribute) is None:
                print("value not set = "+str(physical_attribute))
