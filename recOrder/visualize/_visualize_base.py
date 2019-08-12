# bchhun, {2019-07-24}

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class QChannel(QObject):
    QChannel = pyqtSignal(object)


class VisualizeBase(QObject):

    visualize_signals = [QChannel() for _ in range(20)]

    def __init__(self):
        super(VisualizeBase, self).__init__()

    def get_QChannel(self, index):
        return self.visualize_signals[index]

    # VisualizeBase emitter receivers
    @classmethod
    def emitter(cls, channel=0):

        def emitter_wrap(func):
            def emitter_wrap_func(self, *args, **kwargs):
                out = func(self, *args, **kwargs)
                self.visualize_signals[channel].QChannel.emit(out)
                return func
            emitter_wrap_func.emitter_channel = channel
            return emitter_wrap_func

        return emitter_wrap

    @classmethod
    @pyqtSlot(object)
    def receiver(cls, channel=0):

        def receiver_wrap(func):
            def receiver_wrap_func(self, *args, **kwargs):
                func(self, *args, **kwargs)
                return func
            receiver_wrap_func.receiver_channel = channel
            return receiver_wrap_func

        return receiver_wrap

    @classmethod
    @pyqtSlot(object)
    def bidirectional(cls, emitter_channel=0, receiver_channel=1):

        def bidirectional_wrap(func):
            def bidirectional_wrap_func(self, *args, **kwargs):
                out = func(self, *args, **kwargs)
                self.visualize_signals[emitter_channel].QChannel.emit(out)
                return func
            bidirectional_wrap_func.receiver_channel = receiver_channel
            bidirectional_wrap_func.emitter_channel = emitter_channel
            return bidirectional_wrap_func

        return bidirectional_wrap
