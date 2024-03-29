# bchhun, {2019-07-24}

"""
*** do not use @wraps, which maintains the original function's signature
*** The builder depends on the decorator signature to inspect the class
"""

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class QChannel(QObject):
    QChannel = pyqtSignal(object)


class AnalyzeBase(QObject):

    analysis_signals = [QChannel() for _ in range(30)]

    def __init__(self):
        super(AnalyzeBase, self).__init__()

    def get_QChannel(self, index):
        return self.analysis_signals[index]

    # ============= decorator emitter / receivers ====================
    @classmethod
    def emitter(cls, channel=0):

        def emitter_wrap(func):
            def emitter_wrap_func(self, *args):
                out = func(self, *args)
                cls.analysis_signals[channel].QChannel.emit(out)
                return out
            emitter_wrap_func.emitter_channel = channel
            return emitter_wrap_func

        return emitter_wrap

    @classmethod
    @pyqtSlot(object)
    def receiver(cls, channel=0):

        def receiver_wrap(func):
            def receiver_wrap_func(self, *args):
                func(self, *args)
                return func
            receiver_wrap_func.receiver_channel = channel
            return receiver_wrap_func

        return receiver_wrap

    @classmethod
    @pyqtSlot(object)
    def bidirectional(cls, emitter_channel=0, receiver_channel=1):

        def bidirectional_wrap(func):

            def bidirectional_wrap_func(self, *args):
                out = func(self, *args)
                cls.analysis_signals[emitter_channel].QChannel.emit(out)
                return out
            bidirectional_wrap_func.receiver_channel = receiver_channel
            bidirectional_wrap_func.emitter_channel = emitter_channel

            return bidirectional_wrap_func

        return bidirectional_wrap

    # =============== callable emitter / receivers ==================

    @classmethod
    def emit_on_channel(cls, channel, value):
        cls.analysis_signals[channel].QChannel.emit(value)

    # =============== runnables upon build.run ======================
    @classmethod
    def runnable(cls):

        def runnable_wrap(func):
            def runnable_wrap_func(self, *args, **kwargs):
                func(self, *args, **kwargs)
                return func
            return runnable_wrap_func

        return runnable_wrap


## =======================================
## ========== testcode ===================
class testacq(AnalyzeBase):

    def __init__(self, channel):
        super(testacq, self).__init__()
        self.c = 0
        self.update = AnalyzeBase.emitter(channel=channel)(self.update)

    @AnalyzeBase.emitter(channel = 1)
    def update(self):
        print("calling overridden update")
        self.c += 1
        return self.c


class testrec(AnalyzeBase):

    def __init__(self):
        super(testrec, self).__init__()
        self.c = 0

    @AnalyzeBase.receiver(channel = 1)
    def slot(self, value):
        print("testacq receiver received value "+str(value))


class receiver(QObject):
    """
    standard receiver that doesn't use wrapper
    """

    @pyqtSlot(object)
    def thing(self, value):
        print("receiver received value"+str(value))

    def connection(self, signalemitter):
        signalemitter.acquisition_signal.connect(self.thing)

#todo:
#   tests: decorator with and without parameters
#   tests: above decorator examples
#   tests: normal unit tests
#   tests: decorate non-class bound analyzers (or is this forbidden anyway?)

if __name__ == '__main__':
    t = testacq()
    r = testrec()
    print(t.update.emitter_channel)