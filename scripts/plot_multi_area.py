from glob import glob
from correlation_toolbox import helper as ch
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
    data = np.empty(len(populations), dtype=[("pop", "U10"), ("sim", "U10"), ("value", float)])
    
    # Populate it and return
    data["pop"][:] = populations
    data["sim"][:] = simulators
    data["value"][:] = values
    return data

def remove_junk(axis):
    sns.despine(ax=axis)
    axis.xaxis.grid(False)
    axis.yaxis.grid(False)

def pop_LvR(data_array, t_ref, t_min, t_max, num_neur):
    """
    Compute the LvR value of the given data_array.
    See Shinomoto et al. 2009 for details.

    Parameters
    ----------
    data_array : numpy.ndarray
        Arrays with spike data.
        column 0: neuron_ids, column 1: spike times
    t_ref : float
        Refractory period of the neurons.
    t_min : float
        Minimal time for the calculation.
    t_max : float
        Maximal time for the calculation.
    num_neur: int
        Number of recorded neurons. Needs to provided explicitly
        to avoid corruption of results by silent neurons not
        present in the given data.

    Returns
    -------
    mean : float
        Population-averaged LvR.
    LvR : numpy.ndarray
        Single-cell LvR values
    """
    i_min = np.searchsorted(data_array[0], t_min)
    i_max = np.searchsorted(data_array[0], t_max)
    LvR = np.array([])
    data_array = data_array[:,i_min:i_max]
    for i in np.unique(data_array[1]):
        intervals = np.diff(data_array[0, np.where(data_array[1] == i)[0]])
        if intervals.size > 1:
            val = np.sum((1. - 4 * intervals[0:-1] * intervals[1:] / (intervals[0:-1] + intervals[
                         1:]) ** 2) * (1 + 4 * t_ref / (intervals[0:-1] + intervals[1:])))
            LvR = np.append(LvR, val * 3 / (intervals.size - 1.))
        else:
            LvR = np.append(LvR, 0.0)
    if len(LvR) < num_neur:
        LvR = np.append(LvR, np.zeros(num_neur - len(LvR)))
    return np.mean(LvR), LvR

def calc_correlations(data_array, t_min, t_max, subsample=2000, resolution=1.0):
    # Get unique neuron ids
    ids = np.unique(data_array[1])
    
    # Extract spike train i.e. sorted array of spike times for each neuron
    # **NOTE** this is a version of correlation_toolbox.helper.sort_gdf_by_id, 
    # modified to suit our data format
    ids = np.arange(ids[0], ids[0]+subsample+1000)
    dat = []
    for i in ids:
        dat.append(np.sort(data_array[0, np.where(data_array[1] == i)[0]]))

    # Calculate correlation coefficient
    # **NOTE** this comes from the compute_corrcoeff.py in original paper repository
    bins, hist = ch.instantaneous_spike_count(dat, resolution, tmin=t_min, tmax=t_max)
    rates = ch.strip_binned_spiketrains(hist)[:subsample]
    cc = np.corrcoef(rates)
    cc = np.extract(1-np.eye(cc[0].size), cc)
    cc[np.where(np.isnan(cc))] = 0.
    
    # Return mean correlation coefficient
    return np.mean(cc)
    
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

def calc_stats(duration_s):
    # Does preprocessed data exist?
    rates_exists = path.exists("genn_rates.npy")
    irregularity_exists = path.exists("genn_irregularity.npy")
    corr_coeff_exists = path.exists("genn_corr_coeff.npy")

    # Get list of all data files
    spike_files = list(glob(path.join("genn_recordings", "*.npy")))
    
    # Loop through spike files
    populations = []
    rates = []
    irregularity = []
    correlation = []
    for s in spike_files:
        # Load spike data
        data = np.load(s)
         
        # Extract population name
        pop_name = path.basename(s).split("_")[1].split(".")[0]
        
        # Count spikes
        num_spikes = len(data[0])

        # Count neurons
        num_neurons = int(np.amax(data[1]))
        
        # Add stats to lists
        populations.append(pop_name)
        
        # Calculate rates if data doesn't exist
        if not rates_exists:
            rates.append(num_spikes / (num_neurons * duration_s))
        
        # Calculate irregularity if data doesn't exist
        if not irregularity_exists:
            irregularity.append(pop_LvR(data, 2.0, 500.0, duration_s * 1000.0, num_neurons)[0])
        
        # Calculate correlation coefficient if data doesn't exist
        if not corr_coeff_exists:
            correlation.append(calc_correlations(data, 500.0, duration_s * 1000.0))
    
    # Load rates if they exist, otherwise recalculate
    if rates_exists:
        genn_rates = np.load("genn_rates.npy")
    else:
        genn_rates = create_pop_data_array(populations, "genn", rates)
        np.save("genn_rates.npy", genn_rates)
    
    # Load irregularity if exists, otherwise recalculate
    if irregularity_exists:
        genn_irregularity = np.load("genn_irregularity.npy")
    else:
        genn_irregularity = create_pop_data_array(populations, "genn", irregularity)
        np.save("genn_irregularity.npy", genn_irregularity)
    
    # Load correlation coefficients if exists, otherwise recalculate
    if corr_coeff_exists:
        genn_corr_coeff = np.load("genn_corr_coeff.npy")
    else:
        genn_corr_coeff = create_pop_data_array(populations, "genn", correlation)
        np.save("genn_corr_coeff.npy", genn_corr_coeff)
    
    # Return stats
    return genn_rates, genn_irregularity, genn_corr_coeff

def plot_area(name, axis):
    # Find files containing spikes for this area
    area_spikes = list(reversed(sorted(glob(path.join("genn_recordings", name + "_*.npy")))))

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
    
    axis.set_xlim((3.0, 3.5))
    axis.set_ylim((0.0, np.sum(layer_counts)))
    axis.set_xlabel("Time [s]")

def plot_violin(nest_data, genn_data, axis, vertical, label, lim):
    # Combine GeNN and NEST rates
    data = np.hstack((nest_data, genn_data))
    
    # Calculate order
    order = np.sort(np.unique(data["pop"]))

    # Plot split violin plot
    sns.violinplot(x=data["pop"] if vertical else data["value"], 
                   y=data["value"] if vertical else data["pop"], 
                   hue=data["sim"], split=True, inner="quartile", 
                   ax=axis, order=order)

    # Remove junk
    remove_junk(axis)
    axis.get_legend().remove()

    # Configure axes
    if vertical:
        axis.set_ylabel(label)
        axis.set_ylim(lim)
        plt.setp(axis.get_xticklabels(), ha="center", rotation=90)
    else:
        axis.set_xlabel(label)
        axis.set_xlim(lim)

# Read GeNN and NEST recording paths
assert len(argv) == 2
nest_recording_path = argv[1]
nest_recording_hash = path.split(nest_recording_path)[1]

# Load pre-processed NEST data
nest_rates, areas = load_nest_pop_data(path.join(nest_recording_path, "Analysis", "pop_rates.json"))
nest_corr_coeff = load_nest_pop_data(path.join(nest_recording_path, "Analysis", "corrcoeff.json"), areas)
nest_irregularity = load_nest_pop_data(path.join(nest_recording_path, "Analysis", "pop_LvR.json"), areas)

# Calculate stats from GeNN data
genn_rates, genn_irregularity, genn_corr_coeff = calc_stats(10.5)

# Create plot
fig = plt.figure(figsize=(plot_settings.large_figure[0], plot_settings.medium_figure[1]), frameon=False)

# Create outer gridspec dividing plot area into 3 (2/3 for raster plots, 1/3 for violin plots)
gsp = gs.GridSpec(1, 3)

# Create sub-gridspecs for panels within outer gridspec
violin_plot_gsp = gs.GridSpecFromSubplotSpec(3, 1, subplot_spec=gsp[2], hspace=0.7)
raster_plot_gsp = gs.GridSpecFromSubplotSpec(1, 3, subplot_spec=gsp[0:2])

# Create axes within outer gridspec
v1_axis = plt.Subplot(fig, raster_plot_gsp[0])
v2_axis = plt.Subplot(fig, raster_plot_gsp[1])
fef_axis = plt.Subplot(fig, raster_plot_gsp[2])

# Create axes within violin plot gridspec
rate_violin_axis = plt.Subplot(fig, violin_plot_gsp[0])
corr_coeff_violin_axis = plt.Subplot(fig, violin_plot_gsp[1])
irregularity_violin_axis = plt.Subplot(fig, violin_plot_gsp[2])

# Add axes
fig.add_subplot(v1_axis)
fig.add_subplot(v2_axis)
fig.add_subplot(fef_axis)
fig.add_subplot(rate_violin_axis)
fig.add_subplot(corr_coeff_violin_axis)
fig.add_subplot(irregularity_violin_axis)

# Plot example GeNN raster plots
plot_area("V1", v1_axis)
plot_area("V2", v2_axis)
plot_area("FEF", fef_axis)

vertical = True 

# Combine GeNN and NEST rates and plot split violin plot
plot_violin(nest_rates, genn_rates, rate_violin_axis, 
            vertical, "Rate [spikes/s]", (0.0, 12.0))

# Combine GeNN and NEST correlation coefficients and plot split violin plot
plot_violin(nest_corr_coeff, genn_corr_coeff, corr_coeff_violin_axis, 
            vertical, "Correlation coefficient", (0.0, 0.01))

# Combine GeNN and NEST irregularity and plot split violin plot
plot_violin(nest_irregularity, genn_irregularity, irregularity_violin_axis, 
            vertical, "Irregularity", (0.0, 2.0))

# Label axes
v1_axis.set_title("A: V1", loc="left")
v2_axis.set_title("B: V2", loc="left")
fef_axis.set_title("C: FEF", loc="left")
rate_violin_axis.set_title("D", loc="left")
corr_coeff_violin_axis.set_title("E", loc="left")
irregularity_violin_axis.set_title("F", loc="left")

fig.tight_layout(pad=0)
if not plot_settings.presentation:
    fig.savefig("../figures/multi_area.pdf")
    
# Show plot
plt.show()
