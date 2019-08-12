# bchhun, {2019-07-25}

from PyQt5.QtCore import QRunnable, QThreadPool
from recOrder.acquire import AcquisitionBase
from recOrder.analyze import AnalyzeBase
from recOrder.visualize import VisualizeBase


class ProcessRunnable(QRunnable):
    def __init__(self, target, args):
        super().__init__()
        self.t = target
        self.args = args

    def run(self):
        self.t(*self.args)

    def start(self):
        QThreadPool.globalInstance().start(self)


class Program:

    def __init__(self, acquire=None, analyze=None, visualize=None):
        # register lists of all modules in this application
        self.acq = []
        self.proc = []
        self.vis = []
        self.runnables = []

        # 'register' supplied modules in a list
        if issubclass(acquire.__class__, AcquisitionBase):
            self.acq.append(acquire)
            print("registering "+str(acquire))
        if issubclass(analyze.__class__, AnalyzeBase):
            self.proc.append(analyze)
            print("registering "+str(analyze))
        if issubclass(visualize.__class__, VisualizeBase):
            self.vis.append(visualize)
            print("registering "+str(visualize))

    def add_module(self, module):
        # add more modules to registry
        if issubclass(module.__class__, AcquisitionBase):
            self.acq.append(module)
        if issubclass(module.__class__, AnalyzeBase):
            self.proc.append(module)
        if issubclass(module.__class__, VisualizeBase):
            self.vis.append(module)

    def build(self):
        self._connect_signals()
        self._assign_runnables()

    def _connect_signals(self):
        """
        assigns all signals to all slots between and within modules based on channels
        """
        # acquisition
        for acq in self.acq:
            [self._assign_signal_slot(acq, acq2) for acq2 in self.acq]
            [self._assign_signal_slot(acq, proc) for proc in self.proc]
            [self._assign_signal_slot(acq, vis) for vis in self.vis]

        # process to itself and to visualize
        for proc in self.proc:
            [self._assign_signal_slot(proc, acq) for acq in self.acq]
            [self._assign_signal_slot(proc, proc2) for proc2 in self.proc]
            [self._assign_signal_slot(proc, vis) for vis in self.vis]

        for vis in self.vis:
            [self._assign_signal_slot(vis, acq) for acq in self.acq]
            [self._assign_signal_slot(vis, proc2) for proc2 in self.proc]
            [self._assign_signal_slot(vis, vis2) for vis2 in self.vis]

    def _assign_signal_slot(self, sig, slt):

        sig_dict = self._retrieve_emitter_receiver_attribute(sig, 'emitter')
        slt_dict = self._retrieve_emitter_receiver_attribute(slt, 'receiver')

        # find all functions in sig that are decorated, and their corresponding channels
        for value, key in sig_dict.items():
            emitter_func = getattr(sig, key)

            # find all functions in slt that are decorated, and their corresponding channels
            for value2, key2 in slt_dict.items():
                receiver_func = getattr(slt, key2)

                # check matching channels and connect
                if emitter_func.emitter_channel == receiver_func.receiver_channel:
                    sig.get_QChannel(emitter_func.emitter_channel).QChannel.connect(receiver_func)
                    print("connecting %s to %s " %(str(emitter_func), str(receiver_func)))

    @staticmethod
    def _retrieve_emitter_receiver_attribute(module, socket_type):
        """
        identifies all functions annotated with 'emitter' and 'receiver' and puts these functions in a dictionary

        this dictionary is in {value: key} order to prevent collisions
            values = attributes or function identifier
            key = corresponding attribute or function name

        dictionary is a concatenated group of both __class__ and instance attributes

        * assumption is that there will be collisions if {key:value} is concatenated.
        *   so instead we reverse the dictionary order.
        """
        # this function returns a concatenated dictionary of only those emitter/receiver functions
        if socket_type == 'emitter':
            class_dict = {value: key for key, value in module.__class__.__dict__.items() if
                          ".emitter" in str(value) or ".bidirectional" in str(value)}
            inst_dict = {value: key for key, value in module.__dict__.items() if
                         ".emitter" in str(value) or ".bidirectional" in str(value)}
            class_dict.update(inst_dict)
            return class_dict
        elif socket_type == 'receiver':
            class_dict = {value: key for key, value in module.__class__.__dict__.items() if
                          ".receiver" in str(value) or ".bidirectional" in str(value)}
            inst_dict = {value: key for key, value in module.__dict__.items() if
                         ".receiver" in str(value) or ".bidirectional" in str(value)}
            class_dict.update(inst_dict)
            return class_dict
        else:
            raise ValueError("must supply 'emitter' or 'receiver' as parameter")

    def _assign_runnables(self):
        for acq in self.acq:
            acq_dict = self._retrieve_runnables(acq)
            for value, key in acq_dict.items():
                runnable = getattr(acq, key)
                self.runnables.append(runnable)
        for proc in self.proc:
            proc_dict = self._retrieve_runnables(proc)
            for value, key in proc_dict.items():
                runnable = getattr(proc, key)
                self.runnables.append(runnable)
        for vis in self.vis:
            vis_dict = self._retrieve_runnables(vis)
            for value, key in vis_dict.items():
                runnable = getattr(vis, key)
                self.runnables.append(runnable)

    @staticmethod
    def _retrieve_runnables(module):
        """
        identifies all functions annotated with 'runnable' and puts these functions in a dictionary

        this dictionary is in {value: key} order to prevent collisions
            values = attributes or function identifier
            key = corresponding attribute or function name

        dictionary is a concatenated group of both __class__ and instance attributes

        * assumption is that there will be collisions if {key:value} is concatenated.
        *   so instead we reverse the dictionary order.
        """
        # this function returns a concatenated dictionary of only those runnable functions
        class_dict = {value: key for key, value in module.__class__.__dict__.items() if
                      ".runnable" in str(value)}
        inst_dict = {value: key for key, value in module.__dict__.items() if
                     ".runnable" in str(value)}
        class_dict.update(inst_dict)
        return class_dict

    def run(self):
        for runnable in self.runnables:
            process = ProcessRunnable(target=runnable, args=())
            process.start()


