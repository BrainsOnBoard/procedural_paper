// Standard C++ includes
#include <iostream>
#include <random>

// GeNN robotics includes
#include "analogueRecorder.h"
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
    AnalogueRecorder<scalar> voltages("voltages.csv", VE, Parameters::numExcitatory, ",");

    double wallClock = 0.0;
    {
        TimerAccumulate a(wallClock);
        while(t < 1000.0) {
            // Simulate
            stepTime();

            if(Parameters::recordSpikes) {
                pullECurrentSpikesFromDevice();
                spikes.record(t);
            }

            if(Parameters::recordVoltages) {
                pullVEFromDevice();
                voltages.record(t);
            }
        }
    }

    std::cout << wallClock << ", ";

    spikes.writeCache();

    if(Parameters::timing) {
        std::cout << "Init:" << initTime << std::endl;
        std::cout << "Init sparse:" << initSparseTime << std::endl;
        std::cout << "Neuron update:" << neuronUpdateTime << std::endl;
        std::cout << "Presynaptic update:" << presynapticUpdateTime << std::endl;
    }
    return EXIT_SUCCESS;;
}
