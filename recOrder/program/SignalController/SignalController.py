# #!/usr/bin/env python
# # title           : this_python_file.py
# # description     :This will create a header for a python script.
# # author          :bryant.chhun
# # date            :1/24/19
# # version         :0.0
# # usage           :python this_python_file.py -flags
# # notes           :
# # python_version  :3.6xf
#
# from PyQt5.QtCore import QObject, pyqtSignal
#
# from recOrder.microscope.mm2python_controller import py4j_monitor_LC
# from recOrder.visualize.GUI.NapariWindow import NapariWindow
# from recOrder.program.DataPipe.PipeFromFiles import PipeFromFiles
# from recOrder.visualize.GUI.RecorderWindowControl import RecorderWindowControl
#
# """
# Signal Controller creates all the bindings between emitters/connectors in various classes
# It will also mediate any calculations necessary for emitter-induced events like averaging
# """
#
#
# class SignalController(QObject):
#
#     """
#     Signals to add
#
#     # refactor:
#     pipe from files - set processor
#
#
#     """
#
#     vector_computed = pyqtSignal(object)
#
#     # registered_elements is a dict of (key, value) = (class, list(object))
#     _registered_elements = []
#
#     def __init__(self):
#         super().__init__()
#         self.register(self)
#
#     def register(self, element: object):
#         self._registered_elements.append(element)
#
#     def connect_signals(self):
#         """
#         Loop through all registered classes
#         for each class, call the corresponding function
#
#         Returns
#         -------
#
#         """
#         for element in self._registered_elements:
#             if isinstance(element, NapariWindow):
#                 self._gui_slots(element)
#             if isinstance(element, PipeFromFiles):
#                 self._pipe_slots(element)
#
#     def _gui_slots(self, gui_element):
#         """
#         connects slots from a supplied NapariWindow instance
#             with signals in all other registered classes
#
#         Parameters
#         ----------
#         gui_element : function:
#             NapariWindow instance whose slot is connected to emitter
#
#         Returns
#         -------
#
#         """
#         for element in self._registered_elements:
#             if isinstance(element, PipeFromFiles):
#                 print("connecting pipe to gui")
#                 element.recon_complete.connect(gui_element.update_layer_image)
#
#             # elif isinstance(element, SignalController):
#             #     print("connecting signal controller to gui")
#             #     element.vector_computed.connect(gui_element.update_layer_image)
#
#             elif isinstance(element, RecorderWindowControl):
#                 print("connecting LC calibration to GUI")
#                 element.window_update_signal.connect(gui_element.update_layer_image)
#
#             elif isinstance(element, py4j_monitor_LC):
#                 element.recon_complete.connect(gui_element.update_layer_image)
#
#             else:
#                 print("no matching implementation found for: " + str(type(element)))
#
#     def _pipe_slots(self, pipe_element):
#         """
#         connects slots from supplied PipeFromFiles instance
#             with signals in all other registered classes
#
#         Parameters
#         ----------
#         pipe_element : function:
#             NapariWindow instance whose slot is connected to emitter
#
#         Returns
#         -------
#
#         """
#         for element in self._registered_elements:
#             if isinstance(element, NapariWindow):
#                 # element.average_change.connect(pipe_element.update_average)
#                 pass
#
#
