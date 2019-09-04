# bchhun, {2019-07-25}

"""
This code describes simple execution of Reconstruction and Visualization code.
    Data is received from Micromanager using mm2Python, is processed in this python package,
    and then is displayed in a viewer.
"""


from recOrder.acquisition.RetrieveFiles import RetrieveFiles
from recOrder.analysis.ReconstructOrder import ReconOrder
from recOrder.visualization.RecorderNapariWindow import RecorderNapariWindow
from recOrder.program.BuildProgram import Program
import napari


if __name__ == '__main__':
    with napari.gui_qt():

        # acquisition
        acq = RetrieveFiles()

        # analysis
        processor = ReconOrder(stokes_emitter_channel=1, stokes_recevier_channel=0,
                               physical_emitter_channel=4, physical_receiver_channel=1)

        # visualization
        viewer_window = RecorderNapariWindow()

        program = Program(acquire=acq,
                          analyze=processor,
                          visualize=viewer_window)
        program.build()

        program.run()
