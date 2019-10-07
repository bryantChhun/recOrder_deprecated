# recOrder

record Order (recOrder): A framework for live-processing birefringence data 

# dependencies
* numpy
* py4j
* opencv
* pyqt5
* napari
* ReconstructOrder

pypi install coming soon!

# this repo
recOrder is a framework to enable microscopy acquisition, analysis, and visualization pipelines.  In particular
it is developed to accelerate computational microscopy workflows.

recOrder is an abstraction on top of the pyqt5 backend that simplifies pyqt5's signal/slot mechanism.  recOrder operates
using a concept of "channels" (similar to television or radio channels) whereby any module can broadcast on a channel,
or listen to a channel, without knowing explicitly where the signal is coming from or going to.

please see the examples for a sense of how to construct a program.
In particular, look at "example_reconstruct_order"

## Installation

### Create a new conda environment (optional, but recommended)
>Install conda package management system by installing anaconda or miniconda (https://conda.io/). 
>Creating a conda environment dedicated to ReconstructOrder will avoid version conflicts among packages required by ReconstructOrder and packages required by other python software.
>
>```buildoutcfg
>conda create -n <your-environment-name> python=3.7
>conda activate <your-environment-name>
>```
### pip install via pypi
> (COMING SOON)

## Usage
There are three primary modules in this framework
- acquisition
- analysis
- visualization

And one program construction module:
- program

Acquisition, analysis and visualization contain one base class named AcquisitionBase, AnalysisBase, and VisualizationBase, respectively.

Program contains one class that connects any number of the earlier three modules together.

The typical pattern of usage is to define a class that inherits any of the above bases:

>   ```buildoutcfg
>   class MyTestClass(AcquisitionBase):
>         def __init__(self):
>                super().__init__()
>   ```

Next, to have a class's method broadcast or receive on a channel, simply decorate it:

>   ```buildoutcfg
>   class MyAcquisitionClass(AcquisitionBase):
>          def __init__(self):
>                super().__init__()
>
>           @AcquisitionBase.emitter(channel=0)
>           def broadcast_to_channel():
>                pass
>
>            @AcquisitionBase.receiver(channel=1)
>            der receive_from_channel(from_signal):
>                 pass
>
>   ```

If you want the same method to both receive and broadcast on a channel, use bidirectional:

>   ```buildoutcfg
>   class MyVisualizationClass(VisualizeBase):
>          def __init__(self):
>                super().__init__()
>
>           @VisualizeBase.bidirectional(emitter_channel=1, receiver_channel=0):
>            def emit_and_receive_from_channels(from_signal):
>                pass
>
>   ```

####Note, a method does not need to return a value to emit a signal.  However, a method needs to declare parameter in order to receive a signal.

Finally, to build and run an entire program, use the program class:

>   ```buildoutcfg
>     acq = MyAcquisitionClass()
>     vis = MyVisualizationClass()
>     program = Program(acquire=acq, visualize=vis)
>     program.build()
>   ```

Any number of primary modules can be instantiated and passed to the "program" builder:
program = Program(acquire=<acquisition_module>, analyze=<analysis_module>, visualize=<visualization_module>)
Upon calling "program.build()", signals will be connected and the program is run.


##
For computational microscopy workflows, there are additionally four datastructures and some microscope control utilities:

Four datastructures:
- Intensity
- Stokes
- Physical
- Background

## LICENSE

Chan Zuckerberg Biohub Software License

This software license is the 2-clause BSD license plus clause a third clause
that prohibits redistribution and use for commercial purposes without further
permission.

Copyright © 2019. Chan Zuckerberg Biohub.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1.	Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2.	Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3.	Redistributions and use for commercial purposes are not permitted without
the Chan Zuckerberg Biohub's written permission. For purposes of this license,
commercial purposes are the incorporation of the Chan Zuckerberg Biohub's
software into anything for which you will charge fees or other compensation or
use of the software to perform a commercial service for a third party.
Contact ip@czbiohub.org for commercial licensing opportunities.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.