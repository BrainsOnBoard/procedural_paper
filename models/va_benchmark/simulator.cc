// Standard C++ includes
#include <iostream>
#include <random>

// GeNN robotics includes
#include "timer.h"
#include "spikeRecorder.h"

// Model parameters
#include "parameters.h"

// Auto-generated model code
#include "va_benchmark_CODE/definitions.h"

int main()
{
    allocateMem();
    initialize();
    initializeSparse();

    // Open CSV output files
    SpikeRecorder<SpikeWriterTextCached> spikes(&getECurrentSpikes, &getECurrentSpikeCount, "spikes.csv", ",", true);

    {
        Timer a("Simulation wall clock:");
        while(t < 10000.0) {
            // Simulate
            stepTime();

            pullECurrentSpikesFromDevice();


            spikes.record(t);
        }
    }

    spikes.writeCache();

    std::cout << "Init:" << initTime << std::endl;
    std::cout << "Init sparse:" << initSparseTime << std::endl;
    std::cout << "Neuron update:" << neuronUpdateTime << std::endl;
    std::cout << "Presynaptic update:" << presynapticUpdateTime << std::endl;

    return 0;
}
