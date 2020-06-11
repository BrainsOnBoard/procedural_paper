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
Visual Studio 2015 or later is required 

Tested on Windows 10 with Visual Studio 2019, CUDA 10.1, Python 3.7.7

### Linux

All software dependencies and operating systems (including version numbers)
Versions the software has been tested

Tested on Ubuntu 18.04, GCC 7.5.0, CUDA 10.2 and Python 3.6.9

## Installation guide
### Windows
#### GeNN

#### PyGeNN
### Linux

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