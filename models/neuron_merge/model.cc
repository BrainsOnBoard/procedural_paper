#include "modelSpec.h"

void modelDefinition(NNmodel &model)
{
    model.setDT(1.0);
    model.setName("if_curr");
    model.setTiming(true);
    model.setDefaultVarLocation(VarLocation::DEVICE);
    
    //---------------------------------------------------------------------------
    // Build model
    //---------------------------------------------------------------------------
    // LIF model parameters
    NeuronModels::LIF::ParamValues lifParamVals(1.0, 20.0, -70.0, -70.0, -51.0, 0.0, 2.0);
    NeuronModels::LIF::VarValues lifInitVals(-70.0, 0.0);
    CurrentSourceModels::GaussianNoise::ParamValues csParams(1.0, 0.25);

    // Create IF_curr neuron
    const unsigned int numPops = 10;
    const unsigned int popSize = 1000000 / numPops;
    for(unsigned int i = 0; i < numPops; i++) {
        model.addNeuronPopulation<NeuronModels::LIF>("Excitatory" + std::to_string(i), popSize, lifParamVals, lifInitVals);
        model.addCurrentSource<CurrentSourceModels::GaussianNoise>("ExcitatoryCS" + std::to_string(i), "Excitatory" + std::to_string(i), csParams, {});
    }
}
