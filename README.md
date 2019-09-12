# recOrder

record Order (recOrder): A framework for live-processing birefringence data 

# dependencies
* numpy
* py4j
* opencv
* pyqt5
* napari

pypi install coming soon!

# this repo
please see the examples for a sense of how to construct a program.
In particular, look at "example_reconstruct_order"

# design
There are three primary modules in this framework
- acquisition
- analysis
- visualization

And four datastructures:
- Intensity
- Stokes
- Physical
- Background

Any number of primary modules can be instantiated and passed to the "program" builder:
program = Program(acquire=<acquisition_module>, analyze=<analysis_module>, visualize=<visualization_module>)
Upon calling "program.build()", signals will be connected and the program is run.



