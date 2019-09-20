# bchhun, {2019-08-14}

# framework imports
from recOrder.acquisition.ReconOrderMonitor import ReconOrderMonitor
from recOrder.microscope.mm2python import SnapAndRetrieve
from recOrder.analysis.CalibrationAnalysis import CalibrationAnalysis
from recOrder.analysis.ReconstructOrder import ReconOrder
from recOrder.visualization.RecorderNapariWindow import RecorderNapariWindow
from recOrder.visualization.RecorderWindow import RecorderWindow
from recOrder.visualization.RecorderCalibPlot import RecorderCalibrationDisplay
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from PyQt5 import QtWidgets
from py4j.java_gateway import JavaGateway, GatewayParameters


if __name__ == '__main__':

    gateway = JavaGateway()
    entry_point = gateway.entry_point
    mmc = gateway.entry_point.getCMMCore()

    with napari.gui_qt():
        """
        Channels 01-09: used by ReconOrderMonitor (ch= 9), 
                                ReconstructOrder (ch= 1), 
                                RecorderWindow (ch= 1), 
                                RecorderNapariWindow (ch= 1, 9)
        Channels 10-19: used by ReconOrderMonitor (ch= 10, 11, 19), 
                                ReconstructOrder (ch= 11)
                                RecorderWindow (ch= 10, 11, 19)
        Channels 20-29: used by CalibrationAnalysis (ch= 20 - 26), 
                                RecorderWindow (ch= 20 - 26)
        """

        # acquisition
        # must define the micromanager "channel" names and their corresponding polarization states
        mm_channels = ['State0', 'State1', 'State2', 'State3', 'State4']
        int_dat_channels = ['IExt', 'I90', 'I135', 'I45', 'I0']
        monitor = ReconOrderMonitor(mm_channels, int_dat_channels, gateway)

        snap = SnapAndRetrieve()

        # analysis
        calib = CalibrationAnalysis(gateway)
        ro = ReconOrder(frames=5, swing=0.03)

        # visualization
        viewer_window = RecorderNapariWindow()

        recorder = QtWidgets.QDialog()
        recorder_window = RecorderWindow(recorder, gateway=gateway)
        recorder_plot = RecorderCalibrationDisplay()

        program = Program(acquire=monitor,
                          analyze=calib,
                          visualize=viewer_window)
        program.add_module(recorder_window)
        program.add_module(ro)
        program.add_module(recorder_plot)
        program.add_module(snap)

        program.build()

        # if we define a runnable, call this
        # program.run()
