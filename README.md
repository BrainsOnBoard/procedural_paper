# Larger GPU-accelerated brain simulations with procedural connectivity
Large-scale simulations of spiking neural network models are an important tool for improving our understanding of the dynamics and ultimately the function of brains.
However, even small mammals such as mice have on the order of 1 trillion synaptic connections which, in simulations, are each typically charaterized by at least one floating-point value.
This amounts to several terabytes of data - an unrealistic memory requirement for a single desktop machine.
Large models are therefore typically simulated on distributed supercomputers which is costly and limits large-scale modelling to a few privileged research groups.
In this work, we describe extensions to GeNN - our Graphical Processing Unit (GPU) accelerated spiking neural network simulator - that enable it to 'procedurally' generate connectivity and synaptic weights 'on the go' as spikes are triggered, instead of storing and retrieving them from memory.
We find that GPUs are well-suited to this approach because of their raw computational power which, due to memory bandwidth limitations, is often under-utilised when simulating spiking neural networks.
We demonstrate the value of our approach with a recent model of the Macaque visual cortex consisting of 4.13 million neurons and 24.2 billion synapses.
Using our new method, it can be simulated on a single GPU - a significant step forward in making large-scale brain modelling accessible to many more researchers.
Our results match those obtained on a supercomputer and the simulation runs up to 35% faster on a single high-end GPU than previously on over 1000 supercomputer nodes.

## System requirements
Although GeNN can be used without a CPU, because this paper focusses on GPU acceleration, an NVIDIA GPU with the Kepler architecture or newer required.
Furthermore, to simulate the multi-area model, a GPU with at least 12GB of memory is required (depending on the device and operating system, you may need more memory than this) - it has been tested on an Tesla K80 and a Titan RTX.

### Windows
Visual Studio 2015 or later and Python 3.5 or later is required.

Tested on Windows 10 with Visual Studio 2019, CUDA 10.1 and Python 3.7.7 provided by Anaconda

### Linux


Tested on Ubuntu 18.04; GCC 7.5.0; CUDA 10.0; 10.1 and 10.2; and Python 3.6.9
Tested on Arch Linux, GCC 10.1, CUDA 10.2 and Python 3.8.3

## Installation guide
### Windows
5. From the ``genn directory of this repository, build python extension using ``python setup.py develop``

### Linux
1. Ensure that swig is installed. For example, on an Ubuntu system, run ``sudo apt-get install swig``.
2. Ensure that numpy is installed. For example by running ``pip install numpy``.
2. Ensure the ``CUDA_PATH`` environment variable is set to point to your CUDA installation (e.g. ``/usr/local/cuda``).
3. Ensure that GeNN is in the path. For example, from the ``genn`` directory of this repository, you could run the following in a bash terminal ``set PATH=%PATH%:`pwd`/bin``.
4. From the ``genn directory of this repository, build GeNN libraries with ``make DYNAMIC=1 LIBRARY_DIRECTORY=`pwd`/pygenn/genn_wrapper/``
5. From the ``genn directory of this repository, build python extension using ``python setup.py develop``

Instructions
Typical install time on a "normal" desktop comput

## Demo
Instructions to run on data
Expected output
Expected run time for demo on a "normal" desktop computer

## Instructions for use
How to run the software on your data

### Figure 1
ss
(OPTIONAL) Reproduction instructions