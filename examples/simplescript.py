# bchhun, {2019-08-12}

from recOrder.visualization import VisualizeBase
from recOrder.acquisition import AcquisitionBase
from recOrder.program import Program


class acq(AcquisitionBase):

    @AcquisitionBase.emitter(channel=0)
    def something(self):
        pass

    @AcquisitionBase.runnable()
    def grab_data(self):
        return None


class visual(VisualizeBase):

    @VisualizeBase.receiver(channel=0)
    def something_visual(self):
        pass


if __name__ == "__main__":
    a = acq()
    v = visual()
    p = Program(acquire=a, visualize=v)
    p.build()

    #if a runnable is defined somewhere
    p.run()