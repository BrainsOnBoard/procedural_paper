[![DOI](https://zenodo.org/badge/236798257.svg)](https://zenodo.org/badge/latestdoi/236798257)
# Larger GPU-accelerated brain simulations with procedural connectivity
Simulations are an important tool for investigating brain function but large models are needed to faithfully reproduce the statistics and dynamics of brain activity.
Simulating large spiking neural network models has, until now, required so much memory for storing synaptic connections that it could only be done on high performance computer systems. Here, we present an alternative simulation method we call 'procedural connectivity' where connectivity and synaptic weights are generated 'on the fly' instead of stored and retrieved from memory. This method is particularly well-suited for use on Graphical Processing Units (GPUs) - which are a common fixture in many workstations. Extending our GeNN software with procedural connectivity and a second technical innovation for GPU code generation, we can simulate a recent model of the Macaque visual cortex with 4.13 million neurons and 24.2 billion synapses on a single GPU - a significant step forward in making large-scale brain modelling accessible to more researchers.

## System requirements
Although GeNN can be used without a GPU, because this paper focusses on GPU acceleration, an NVIDIA GPU with the Kepler architecture or newer is required.
Furthermore, to simulate the multi-area model, a GPU with at least 12GB of memory is required (depending on the device and operating system, you may need more memory than this) - it has been tested on an Tesla K80 and a Titan RTX.

### Windows
To build GeNN, Visual Studio 2015 or later and Python 3.5 or later is required.
The version of GeNN included in this repository has been tested with:
* Windows 10 with Visual Studio 2019, CUDA 10.1 and Python 3.7.7 provided by Anaconda
* Windows 10 with Visual Studio 2017, CUDA 10.1 and Python 3.7.0 provided by Anaconda

### Linux
To build GeNN, GCC 4.9.1 or later and Python 2.7 or later is required.
The version of GeNN included in this repository has been tested with:
* Ubuntu 18.04; GCC 7.5.0; CUDA 10.0; 10.1 and 10.2; and Python 3.6.9
* Arch Linux, GCC 10.1, CUDA 10.2 and Python 3.8.3

## Installation guide
Installation should take less than 5 minutes on a standard PC.
We recommend using [python virtualenvs](https://pypi.org/project/virtualenv/) to prevent conflicts between installed python package versions.

### Windows
These instructions assume that the Anaconda platform was used to install Python, but it _should_ be possible to install PyGeNN using suitable versions of Python installed in a different way.
1. Start a command prompt with the correct Visual Studio environment. For example, if you are using Visual Studio 2019, you would select ``Start -> Visual Studio 2019 -> x64 Native Tools Command Prompt``.
2. Activate your chosen version of Anaconda. For example, if your user is called "me" and Anaconda is installed in your home directory, you might run ``c:\Users\Me\Anaconda3\Scripts\activate.bat c:\Users\Me\Anaconda3``.
3. Clone this repository using ``git clone --recursive https://github.com/BrainsOnBoard/procedural_paper.git``
4. Ensure that swig is installed. For example, if you are using Anaconda, run ``conda install swig``.
5. Ensure that numpy is installed. For example by running ``pip install numpy``.
6. Ensure that the version of GeNN included in this repository is in the path. For example, if your user is called "me" and this repository is located in Documents, you could run the following in the terminal ``SET "PATH=%PATH%;c:\Users\me\Documents\procedural_paper\genn\bin"``.
7. From the ``genn`` directory of this repository, build GeNN libraries with ``msbuild genn.sln /t:Build /p:Configuration=Release_DLL``
8. From the ``genn`` directory of this repository, copy the GeNN libraries into the correct location with ``copy /Y lib\genn*Release_DLL.* pygenn\genn_wrapper``
9. From the ``genn`` directory of this repository, build python extension using ``python setup.py develop``

### Linux
1. Clone this repository using ``git clone --recursive https://github.com/BrainsOnBoard/procedural_paper.git``
2. Ensure that swig is installed. For example, on an Ubuntu system, run ``sudo apt-get install swig``.
3. Ensure that numpy is installed. For example by running ``pip install numpy``.
4. Ensure the ``CUDA_PATH`` environment variable is set to point to your CUDA installation. For example from a bash terminal you could run ``export CUDA_PATH=/usr/local/cuda``.
5. Ensure that the version of GeNN included in this repository is in the path. For example, from the ``genn`` directory of this repository, you could run the following in a bash terminal ``PATH=$PATH:`pwd`/bin``.
6. From the ``genn`` directory of this repository, build GeNN libraries with ``make DYNAMIC=1 LIBRARY_DIRECTORY=`pwd`/pygenn/genn_wrapper/``
7. From the ``genn`` directory of this repository, build python extension using ``python setup.py develop``

## Demo
To demonstrate your newly installed version of GeNN, you can run the GeNN implementation of [The Cell-Type Specific Cortical Microcircuit](http://www.ncbi.nlm.nih.gov/pubmed/23203991) developed by Tobias C. Potjans and Markus Diesmann, previously discussed in [our paper](https://www.frontiersin.org/articles/10.3389/fnins.2018.00941).
This should take less than 2 minutes on a standard PC.

### Windows
1. Navigate to the ``genn/userproject/PotjansMicrocircuit_project`` directory of this repository.
2. Build the project runner executable with ``msbuild ..\userprojects.sln /t:generate_potjans_microcircuit_runner /p:Configuration=Release``
3. Build and simulate the project with ``generate_run test`` where "test" is the name of the directory to save the model output.
4. Plot results with ``python plot.py test`` where "test" is again the name of the directory to save the model output.

### Linux
1. Navigate to the ``genn/userproject/PotjansMicrocircuit_project`` directory of this repository.
2. Build the project runner executable with ``make``
3. Build and simulate the project with ``./generate_run test`` where "test" is the name of the directory to save the model output.
4. Plot results with ``python plot.py test`` where "test" is again the name of the directory to save the model output.

A raster plot resembling this one should then be displayed:
![Microcircuit output](microcircuit_demo.png)

## Instructions for use
If you are interested in using GeNN for simulating your own models please see the [user manual](https://genn-team.github.io/genn/documentation/4/html/index.html) or the [tutorial](https://github.com/neworderofjamie/new_genn_tutorials).
To reproduce the figures included in this paper, please follow the steps below.

### Reproducing figure 1
Instructions for simulating model are included in a seperate [readme](models/va_benchmark/README.md)
Data points can be added to [scaling_data.csv](scripts/scaling_data.csv) and then plotted using [plot_performance_scaling.py](scripts/plot_performance_scaling.py).

### Reproducing figure 2
Instructions for simulating model are included in a seperate [readme](models/neuron_merge/README.md)
Data points can be added to [merging_data.csv](scripts/merging_data.csv) and then plotted using [plot_merging_scaling.py](scripts/plot_merging_scaling.py).

### Reproducing figure 3
Install additional python dependencies using ``pip install -r models/multi-area-model/requirements.txt``.
The "ground state" simulation can be run using the [run_example_fullscale.py](https://github.com/neworderofjamie/multi-area-model/blob/master/run_example_fullscale.py) script and the "resting state" simulation using [run_example_1_9_fullscale.py](https://github.com/neworderofjamie/multi-area-model/blob/master/run_example_1_9_fullscale.py) script.
Both simulations will write spiking data into the [simulations](https://github.com/neworderofjamie/multi-area-model/blob/master/simulations) directory.
The spiking statistics shown in figure 3 can be calculated from these spike trains or those downloaded from https://doi.org/10.25377/sussex.12912699 using the [calc_multi_area_stats.py](scripts/calc_multi_area_stats.py) script. For example:
```
python calc_multi_area_stats.py 82d3c0816b0ad1c07ea27e61eb981f7a_seed_1 10.5
```
will calculate both per-neuron and population averaged spike statistics from the GeNN simulation output in the `82d3c0816b0ad1c07ea27e61eb981f7a_seed_1` directory, based on a simulation duration of 10.5 seconds.
The population averaged spike statistics produced by this script can then be plotted using the [plot_multi_area.py](scripts/plot_multi_area.py) script.

### Reproducing figure 4
The per-neuron spike statistics produced by the [calc_multi_area_stats.py](scripts/calc_multi_area_stats.py) script are used as the input to the [calc_pairwise_histograms.py](scripts/calc_pairwise_histograms.py) script which calculates the histograms used for this figure. For example:
```
python calc_pairwise_histograms.py seed_1 seed_2
```
will calculate histograms suitable for comparing the stats of a simulation in the ``seed_1`` directory against another in the ``seed_2`` directory and produce ``seed_1_seed_2_XX.npy`` files for each population which can be plotted using the [plot_multi_area_kl_divergence.py](scripts/plot_multi_area_kl_divergence.py) script.
