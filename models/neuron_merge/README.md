# Model used to produce figure 2
## Building and running
First set the number of populations to test on line 21 of model.cc then build and run model:

### Windows
```
genn-buildmodel.bat model.cc
msbuild /m /verbosity:minimal /p:Configuration=Release if_curr.sln
if_curr_Release
```

### Linux/Mac
```
genn-buildmodel.sh model.cc
make
./if_curr
```

"Tsim" will be outputted by the simulation, "Tcomp" can be recorded using standard operating system tools (e.g. ``time`` on Linux) and the executable can be run using [Nsight Compute](https://developer.nvidia.com/nsight-compute) to calculate "Kmem" and "Nstall".