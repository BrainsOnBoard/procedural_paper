from glob import glob
from matplotlib import gridspec as gs
from matplotlib import pyplot as plt
import json
import numpy as np
import seaborn as sns
from os import path
from six import iteritems
from sys import argv
import plot_settings

def create_pop_data_array(populations, simulators, values):
    # Create suitable numpy array
    data = np.empty(len(populations), dtype=[("pop", "a10"), ("sim", "a10"), ("value", float)])
    
    # Populate it and return
    data["pop"][:] = populations
    data["sim"][:] = simulators
    data["value"][:] = values
    return data

def remove_junk(axis):
    sns.despine(ax=axis)
    axis.xaxis.grid(False)
    axis.yaxis.grid(False)
    
def load_nest_pop_data(filename, areas=None):
    # Load JSON format
    data_json = json.load(open(filename, 'r'))
    
    # Create default dict for data
    populations = []
    values = []
    
    # If areas aren't passed, extract them
    area_names = areas
    if area_names is None:
        area_names = data_json["Parameters"]["areas"]
        
    # Loop through areas included in data
    for a in area_names:
        # Loop through populations in area
        for p, d in iteritems(data_json[a]):
            # Ignore "total"
            if p != "total":
                populations.append(p)
                
                # If it's iterable, add first
                try:
                    iter(d)
                    values.append(d[0])
                # Otherwise, add value
                except TypeError:
                    values.append(d)
    
    # Create and populate numpy array of data
    data = create_pop_data_array(populations, "nest", values)
    
    # If no areas were passed, return data and areas
    if areas is None:
        return data, area_names
    # Otherwise, just return data
    else:
        return data

def calc_stats(genn_recording_path, duration_s=2.0):
    # Get list of all data files
    spike_files = list(glob(path.join(genn_recording_path, "*.npy")))
    
    # Loop through spike files
    populations = []
    rates = []
    for s in spike_files:
        # Load spike data
        data = np.load(s)
         
        # Extract population name
        pop_name = path.basename(s).split("_")[1].split(".")[0]
        
        # Count spikes
        num_spikes = len(data[0])

        # Count neurons
        num_neurons = int(np.amax(data[1]))
        
        populations.append(pop_name)
        rates.append(num_spikes / (num_neurons * duration_s))
    
    return create_pop_data_array(populations, "genn", rates)

def plot_area(genn_recording_path, name, axis):
    # Find files containing spikes for this area
    area_spikes = list(reversed(sorted(glob(path.join(genn_recording_path, name + "_*.npy")))))

    # Extract names of sub-populations from filenames
    pop_names = [path.basename(s).split("_")[1].split(".")[0] for s in area_spikes]
    assert all(a[-1] == "I" for a in pop_names[::2])
    assert all(a[-1] == "E" for a in pop_names[1::2])

    # Loop through area spike files and population names
    start_id = 0
    layer_counts = np.zeros(len(pop_names) // 2, dtype=int)
    for i, (s, n)  in enumerate(zip(area_spikes, pop_names)):
        data = np.load(s)
        
        # Approx
        num = int(np.amax(data[1]))

        # Add num to layer count
        layer_counts[i // 2] += num

        num_spikes = len(data[0])
        indices = np.random.choice(num_spikes, int(round(num_spikes * 0.03)))

        # Plot spikes
        is_inhibitory = n[-1] == "I"
        axis.scatter(data[0][indices] / 1000.0, data[1][indices] + start_id, s=2,
                     edgecolors="none", color="firebrick" if is_inhibitory else "navy")

        # Update offset
        start_id += num

    # Label layers
    axis.set_yticks(np.cumsum(layer_counts) - (layer_counts / 2))
    axis.set_yticklabels(["L" + n[:-1] for n in pop_names[::2]])
    remove_junk(axis)
    
    axis.set_xlim((1.5, 2.0))
    axis.set_ylim((0.0, np.sum(layer_counts)))
    axis.set_xlabel("Time [s]")

# Read GeNN and NEST recording paths
assert len(argv) == 3
genn_recording_path = argv[1]
nest_recording_path = argv[2]
nest_recording_hash = path.split(nest_recording_path)[1]

# Load pre-processed NEST data
nest_rates, areas = load_nest_pop_data(path.join(nest_recording_path, "Analysis", "pop_rates.json"))
nest_corr_coeff = load_nest_pop_data(path.join(nest_recording_path, "Analysis", "corrcoeff.json"), areas)
nest_irregularity = load_nest_pop_data(path.join(nest_recording_path, "Analysis", "pop_LvR.json"), areas)

# Calculate stats from GeNN data
genn_rates = calc_stats(genn_recording_path)

# Create plot
fig = plt.figure(figsize=(plot_settings.large_figure[0], plot_settings.medium_figure[1]), frameon=False)

# Create outer gridspec dividing plot area into 4
gsp = gs.GridSpec(1, 4)

# Create sub-gridspecs for each panel of violin plots
violin_plot_gsp = gs.GridSpecFromSubplotSpec(3, 1, subplot_spec=gsp[3])

# Create axes within outer gridspec
v1_axis = plt.Subplot(fig, gsp[0])
v2_axis = plt.Subplot(fig, gsp[1])
fef_axis = plt.Subplot(fig, gsp[2])

# Add axes within outer gridspec
fig.add_subplot(v1_axis)
fig.add_subplot(v2_axis)
fig.add_subplot(fef_axis)

# Create axes within violin plot gridspec
rate_violin_axis = plt.Subplot(fig, violin_plot_gsp[0])
corr_coeff_violin_axis = plt.Subplot(fig, violin_plot_gsp[1])
irregularity_violin_axis = plt.Subplot(fig, violin_plot_gsp[2])

# Add axes within violin plot gridspec
fig.add_subplot(rate_violin_axis)
fig.add_subplot(corr_coeff_violin_axis)
fig.add_subplot(irregularity_violin_axis)

# Plot example GeNN raster plots
plot_area(genn_recording_path, "V1", v1_axis)
plot_area(genn_recording_path, "V2", v2_axis)
plot_area(genn_recording_path, "FEF", fef_axis)

# Combine GeNn and NEST rates and plot violin plot
rates = np.hstack((nest_rates, genn_rates))
sns.violinplot(x=rates["value"], y=rates["pop"], hue=rates["sim"],
               split=True, inner="quartile", ax=rate_violin_axis)
remove_junk(rate_violin_axis)
rate_violin_axis.get_legend().remove()

sns.violinplot(x=nest_corr_coeff["value"], y=nest_corr_coeff["pop"],
               ax=corr_coeff_violin_axis)
remove_junk(corr_coeff_violin_axis)
#corr_coeff_violin_axis.get_legend().remove()

sns.violinplot(x=nest_irregularity["value"], y=nest_irregularity["pop"],
               ax=irregularity_violin_axis)
remove_junk(irregularity_violin_axis)
#irregularity_violin_axis.get_legend().remove()

# Label axes
v1_axis.set_title("A: V1", loc="left")
v2_axis.set_title("B: V2", loc="left")
fef_axis.set_title("C: FEF", loc="left")
rate_violin_axis.set_title("D", loc="left")
corr_coeff_violin_axis.set_title("E", loc="left")
irregularity_violin_axis.set_title("F", loc="left")

fig.tight_layout(pad=0)

# Show plot
plt.show()
