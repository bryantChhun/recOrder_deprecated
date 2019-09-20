# bchhun, {2019-09-18}

from recOrder.visualization._visualize_base import VisualizeBase
from recOrder.utils.QThreader import ProcessRunnable

import matplotlib.pyplot as plt
import numpy as np
plt.ion()


class RecorderCalibrationDisplay(VisualizeBase):

    def __init__(self):
        super().__init__()
        self.x_sample = None
        self.y_value = None

    @VisualizeBase.receiver(channel=20)
    def new_calibration_plot(self, param):
        p = ProcessRunnable(target=self._build_display, args=())
        p.start()

    def _build_display(self):
        self.__init__()

        self.data = None
        self.x_sample = np.array([0])
        self.y_value = np.array([0])

        self.fig, self.ax = plt.subplots()
        self.lines, = self.ax.plot([], [], marker='o', linestyle='-')
        self.lines.set_dashes([2,2,2,2])

        self.ax.set(xlabel="frame number", ylabel="intensit y",
                    title="mean intensity during calibration")

        self.lines.set_xdata(self.x_sample)
        self.lines.set_ydata(self.y_value)

        self.ax.set_autoscaley_on(True)
        self.ax.set_ylim(0, 65536)

        self.ax.grid()

        plt.show()

    @VisualizeBase.receiver(channel=4)
    def update(self, value):
        # append y value
        self.y_value = np.append(self.y_value, np.mean(value))

        # increment x sample
        self.x_sample = np.append(self.x_sample, self.x_sample[-1]+1)

        # place new data
        # self.ax.plot(self.x_sample, self.y_value)
        self.lines.set_xdata(self.x_sample)
        self.lines.set_ydata(self.y_value)
        self.lines.set_dashes([2,2,2,2])

        self.ax.relim()
        self.ax.autoscale_view()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
