# Model used to produce figure 1
## Building and running
First configure ``numNeurons``, ``presynapticParallelism``, ``proceduralConnectivity`` and ``bitmaskConnectivity`` in parameters.h then build and run model:

### Windows
```
genn-buildmodel.bat model.cc
msbuild /m /verbosity:minimal /p:Configuration=Release va_benchmark.sln
va_benchmark_Release
```

### Linux/Mac
```
genn-buildmodel.sh model.cc
make
./va_benchmark
```