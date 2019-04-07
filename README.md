# recOrder

record Order: A module for live-processing birefringence data 

note: needs lots of cleanup and removal of deprecated functions

# dependencies
* numpy
* py4j
* opencv
* pyqt5
* napari

Note: current napari distribution is 0.0.6.  This will NOT contain necessary elements to for recOrder.

Instead, please do the following:

1) create a new environment for python 3.7 (conda create -n myenvname python=3.7)
2) clone the repo (https://github.com/napari/napari)
3) navigate to the napari folder and type, in order:
  - 3a. "pip install -r requirements.txt"
  - 3b. "pip install -e ." !!!(don't forget the . )!!!
4) within pycharm, from your recOrder repo, navigate to your "project structure" under "preferences"
  - 4a. click "add content root" and select the napari repo

In the future, when napari pushes a distribution that includes vector layers, you will be able to pip install all dependencies


# this repo
To get a sense of the API, look at the tests:
- 'testReconOrder_mse_sim' for simulated, non-background corrected data
- 'testReconOrder_mse' for real data, including background correction

the "construct_all" method establishes all elements of the pipeline and executes reconstruction:
1) create one of the "DataPipe" objects
2) create one of the "Processing" objects (ReconOrder is the only that's properly implemented)
- 2a) set any processor properties
3) connect the processor to the datapipe
- 3a) call any setup functions in the datapipe
4) call datapipe's "run_reconstruction"

# design
There are five modules and four datastructures in this repo:
- FileManagement: to load data from files or sockets (py4j)
- Datapipe: connects data from FileManagement to GUI and/or Processor
- GUI: napari visualization and ReconOrder microscopy control
- Processor: for processing data 
- Signal Controller: connects and manages signals from some of the above modules

# usage
The DataPipe modules are the only which contain data.  Processor and GUI simply input/output data.
There are primarily four data structures:
- IntensityData
- StokesData
- PhysicalData
- BackgroundData (inherits the above three)

The DataPipe holds current instances of each of these four, for a given set of loaded data.

For background correction, you need only create two datapipes.  All reconstruction can be done from the same instance that is bound to each datapipe


