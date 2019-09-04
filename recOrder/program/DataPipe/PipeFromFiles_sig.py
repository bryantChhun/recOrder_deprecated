#
# from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool, QRunnable
#
# from recOrder.datastructures.BackgroundData import BackgroundData
# from recOrder.datastructures.IntensityData import IntensityData
# from recOrder.datastructures.PhysicalData import PhysicalData
# from recOrder.datastructures.StokesData import StokesData
# from recOrder.acquisition.FileManagement.RetrieveFiles import RetrieveData
# from recOrder.analysis.Processing.ReconOrder import ReconOrder
#
# from datetime import datetime
#
# """
# PipeFromFiles is a communication interface between data retrieval method "RetrieveFiles" (under "FileManagement")
#   and any of the other modules under GUI, Processor
# """
#
#
# def timer(func):
#     def timer_wrap(*args, **kwargs):
#         start = datetime.now()
#         func(*args,**kwargs)
#         stop = datetime.now()
#         print("\t"+str((stop-start).microseconds))
#     return timer_wrap
#
#
# class ProcessRunnable(QRunnable):
#     def __init__(self, target, args):
#         QRunnable.__init__(self)
#         self.t = target
#         self.args = args
#
#     def run(self):
#         self.t(*self.args)
#
#     def start(self):
#         QThreadPool.globalInstance().start(self)
#
#
# class PipeFromFiles(QObject):
#
#     recon_complete = pyqtSignal(object)
#
#     def __init__(self,  type = "Test", sample_type = "Sample1"):
#         super().__init__()
#         self.type = type
#         self.sample_type = sample_type
#         self.retrieve_file = RetrieveData()
#         self.intensity = IntensityData()
#         self.stokes = StokesData()
#         self.physical = PhysicalData()
#         self.background = BackgroundData()
#         self._Recon = None
#
#     def set_processor(self, processor):
#         if isinstance(processor, ReconOrder):
#             self._Recon = processor
#             return True
#         else:
#             self._Recon = None
#             raise ValueError("processor wrong type")
#
#     def get_processor(self):
#         return self._Recon
#
#     @timer
#     def fetch_images(self):
#         print('fetching images')
#         self.intensity.IExt = self.retrieve_file.get_array_from_filename('State0', type=self.type, sample_type=self.sample_type)
#         self.intensity.I90 = self.retrieve_file.get_array_from_filename('State1', type=self.type, sample_type=self.sample_type)
#         self.intensity.I135 = self.retrieve_file.get_array_from_filename('State2', type=self.type, sample_type=self.sample_type)
#         self.intensity.I45 = self.retrieve_file.get_array_from_filename('State3', type=self.type, sample_type=self.sample_type)
#         if self._Recon.frames == 5:
#             self.intensity.I0 = self.retrieve_file.get_array_from_filename('State4', type=self.type, sample_type=self.sample_type)
#
#         return True
#
#     @timer
#     def compute_stokes(self):
#         print("compute stokes")
#         self.stokes = self._Recon.compute_stokes(self.intensity)
#         return True
#
#     @timer
#     def reconstruct_image(self):
#         print("Reconstruct image")
#         self.physical = self._Recon.compute_physical(self.stokes)
#         return True
#
#     @timer
#     def rescale_bitdepth(self):
#         print("rescaling bitdepth for display")
#         self.physical = self._Recon.rescale_bitdepth(self.physical)
#         return True
#
#     @timer
#     def compute_inst_matrix(self):
#         print("compute inst matrix")
#         self._Recon.compute_inst_matrix()
#         return True
#
#     @timer
#     def correct_background(self, background : object):
#         print("correct background")
#         self._Recon.correct_background(self.stokes, background)
#         return True
#
#     # the lower two methods do not call the private recon attribute.
#     def build_background(self):
#         self.background.assign_intensity(self.intensity)
#         self.background.assign_stokes(self.stokes)
#         self.background.assign_physical(self.physical)
#
#     def fetch_stokes_physical(self):
#         print('fetch stokes physical')
#         self.fetch_images()
#
#         self.compute_inst_matrix()
#         self.compute_stokes()
#         self.reconstruct_image()
#
#         self.build_background()
#
#     def fetch_stokes_physical_bgcorr(self, background: BackgroundData):
#         '''
#         Performs both standard background correction from BG images AND
#             local background correction using GaussianBlur
#         :param background: ReconOrder object that contains stokes calculations for BG images
#         :return: True if successful
#         '''
#         self.fetch_stokes_physical()
#         self.correct_background(background)
#         self.rescale_bitdepth()
#         self.recon_complete.emit(self.physical)
#
#     '''
#     Threads for running reconstruction.  Needed to prevent blocking UI.
#         Pyqt slots/signals will notify UI that data is ready.
#     '''
#     def run_reconstruction(self, threaded = False):
#         if threaded:
#             print('starting thread')
#             self.process = ProcessRunnable(target=self.fetch_stokes_physical, args=())
#             self.process.start()
#         else:
#             print("\t bg calculation")
#             self.fetch_stokes_physical()
#
#     def run_reconstruction_BG_correction(self, background : BackgroundData, threaded = False):
#         if threaded:
#             self.process = ProcessRunnable(target=self.fetch_stokes_physical_bgcorr, args=(background,))
#             self.process.start()
#         else:
#             print('\n Sample Reconstruction')
#             self.fetch_stokes_physical_bgcorr(background)
