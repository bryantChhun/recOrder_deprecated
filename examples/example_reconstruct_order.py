# bchhun, {2019-08-14}

# framework imports
from recOrder.acquisition.ReconOrderMonitor import ReconOrderMonitor
from recOrder.analysis.CalibrationAnalysis import CalibrationAnalysis
from recOrder.analysis.ReconstructOrder import ReconOrder
from recOrder.visualization.SimpleNapariWindow import SimpleNapariWindow
from recOrder.visualization.RecorderNapariWindow import RecorderNapariWindow
from recOrder.visualization.RecorderWindow import RecorderWindow
from recOrder.program.BuildProgram import Program

# additional imports
import napari
from PyQt5 import QtWidgets
from py4j.java_gateway import JavaGateway, GatewayParameters


if __name__ == '__main__':

    gateway = JavaGateway()
    entry_point = gateway.entry_point
    mmc = gateway.entry_point.getCMMCore()

    # mmc.setProperty('MeadowlarkLcOpenSource', 'Wavelength', str(532))

    with napari.gui_qt():
        """
        Channels 01-09: used by ReconOrderMonitor (ch=9), 
                                ReconstructOrder (ch=1), 
                                RecorderWindow (ch=1), 
                                RecorderNapariWindow (ch=1,9)
        Channels 10-19: used by ReconOrderMonitor, ReconstructOrder, RecorderWindow
        Channels 20-29: used by CalibrationAnalysis, RecorderWindow
        """

        # acquisition
        # create acquisition module for calibration
        mm_channels = ['State0', 'State1', 'State2', 'State3', 'State4']
        int_dat_channels = ['IExt', 'I90', 'I135', 'I45', 'I0']
        monitor = ReconOrderMonitor(mm_channels, int_dat_channels, gateway)

        # analysis
        calib = CalibrationAnalysis(gateway)
        ro = ReconOrder(frames=5, swing=0.03)

        # visualization
        # these visualization windows are fine
        viewer_window = RecorderNapariWindow()
        # viewer_window = SimpleNapariWindow(window_channel=13)
        recorder = QtWidgets.QDialog()
        recorder_window = RecorderWindow(recorder, gateway=gateway)

        program = Program(acquire=monitor,
                          analyze=calib,
                          visualize=viewer_window)
        program.add_module(recorder_window)
        program.add_module(ro)

        program.build()

        # will launch the monitor.  let's let the button launch this instead
        # program.run()
