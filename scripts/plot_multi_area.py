from glob import glob
from itertools import repeat
from matplotlib import gridspec as gs
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
import json
import numpy as np
import seaborn as sns
from copy import copy
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
    sns.despine(ax=axis, left=True, bottom=True)
    axis.xaxis.grid(False)

def load_pop_data(stat_file_stem, simulator_prefix, data_path):
    # Create default dict for data
    populations = []
    values = []
    
    # Get list of files containing data for this
    data_files = list(glob(path.join(data_path, "%s_%s_*.npy" % (simulator_prefix, stat_file_stem))))
    for d in data_files:
        # Extract pop name
        pop_name = path.splitext(d)[0].split("_")[-1]
        
        # Load data
        data = np.load(d)
        
        # Ad to arrays
        populations.extend(repeat(pop_name, len(data)))
        values.extend(data)
    
    # Create and populate numpy array of data
    return create_pop_data_array(populations, simulator_prefix, values)

def plot_area(name, axis, data_path):
    # Find files containing spikes for this area
    area_spikes = list(reversed(sorted(glob(path.join(data_path, "genn_recordings", name + "_*.npy")))))

    # Extract names of sub-populations from filenames
    pop_names = [path.basename(s).split("_")[1].split(".")[0] for s in area_spikes]
    assert all(a[-1] == "I" for a in pop_names[::2])
    assert all(a[-1] == "E" for a in pop_names[1::2])

    # Loop through area spike files and population names
    start_id = 0
    layer_counts = np.zeros(len(pop_names) // 2, dtype=int)
    excitatory_actor = None
    inhibitory_actor = None
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
        actor = axis.scatter(data[0][indices] / 1000.0, data[1][indices] + start_id, s=2,
                             rasterized=True, edgecolors="none", 
                             color="firebrick" if is_inhibitory else "navy")

        # Store actors
        if is_inhibitory:
            inhibitory_actor = actor
        else:
            excitatory_actor = actor

        # Update offset
        start_id += num

    # Label layers
    axis.set_yticks(np.cumsum(layer_counts) - (layer_counts / 2))
    axis.set_yticklabels(["L" + n[:-1] for n in pop_names[::2]])
    remove_junk(axis)
    axis.yaxis.grid(False)
    
    axis.set_xlim((3.0, 3.5))
    axis.set_ylim((0.0, np.sum(layer_counts)))
    axis.set_xlabel("Time [s]")
    
    return copy(excitatory_actor), copy(inhibitory_actor)

def plot_violin(nest_data, genn_data, axis, vertical, label, lim):
    # Combine GeNN and NEST rates
    data = np.hstack((nest_data, genn_data))
    
    # Calculate order
    order = np.sort(np.unique(data["pop"]))

    # Plot split violin plot
    sns.violinplot(x=data["pop"] if vertical else data["value"], 
                   y=data["value"] if vertical else data["pop"], 
                   hue=data["sim"], split=True, inner="quartile", 
                   linewidth=0.75, cut=0.0, ax=axis, order=order)

    # Remove junk
    axis.minorticks_on()
    remove_junk(axis)
    axis.yaxis.grid(True, "both")
    axis.get_legend().remove()

    # Configure axes
    if vertical:
        axis.set_ylabel(label)
        axis.set_ylim(lim)
        plt.setp(axis.get_xticklabels(), ha="center", rotation=90)
    else:
        axis.set_xlabel(label)
        axis.set_xlim(lim)

# Load pre-processed NEST data
nest_rates_1_0 = load_pop_data("rates", "nest", "chi_1_0")
nest_irregularity_1_0 = load_pop_data("irregularity", "nest", "chi_1_0")
nest_corr_coeff_1_0 = load_pop_data("corr_coeff", "nest", "chi_1_0")
nest_rates_1_9 = load_pop_data("rates", "nest", "chi_1_9")
nest_irregularity_1_9 = load_pop_data("irregularity", "nest", "chi_1_9")
nest_corr_coeff_1_9 = load_pop_data("corr_coeff", "nest", "chi_1_9")

# Load pre-processed GeNN data
genn_rates_1_0 = load_pop_data("rates", "genn", "chi_1_0")
genn_irregularity_1_0 = load_pop_data("irregularity", "genn", "chi_1_0")
genn_corr_coeff_1_0 = load_pop_data("corr_coeff", "genn", "chi_1_0")
genn_rates_1_9 = load_pop_data("rates", "genn", "chi_1_9")
genn_irregularity_1_9 = load_pop_data("irregularity", "genn", "chi_1_9")
genn_corr_coeff_1_9 = load_pop_data("corr_coeff", "genn", "chi_1_9")

# Create plot
fig = plt.figure(frameon=False, figsize=(17.0 * plot_settings.cm_to_inches, 
                                         18.0 * plot_settings.cm_to_inches))

# Create outer gridspec with three columns
gsp = gs.GridSpec(1, 3)

# Create two sub-gridspecs to divide these columns into gridspecs for raster and violin plots with an axis for each regime
raster_gsp = gs.GridSpecFromSubplotSpec(2, 1, subplot_spec=gsp[0:2], hspace=0.3)
violin_gsp = gs.GridSpecFromSubplotSpec(2, 1, subplot_spec=gsp[2], hspace=0.3)

# Create four more gridspecs to divide each of these gridspecs into individual axes for plots
violin_plot_1_0_gsp = gs.GridSpecFromSubplotSpec(3, 1, subplot_spec=violin_gsp[0], hspace=0.9)
raster_plot_1_0_gsp = gs.GridSpecFromSubplotSpec(1, 3, subplot_spec=raster_gsp[0])
violin_plot_1_9_gsp = gs.GridSpecFromSubplotSpec(3, 1, subplot_spec=violin_gsp[1], hspace=0.9)
raster_plot_1_9_gsp = gs.GridSpecFromSubplotSpec(1, 3, subplot_spec=raster_gsp[1])

# Create axes within outer gridspec
v1_1_0_axis = plt.Subplot(fig, raster_plot_1_0_gsp[0])
v2_1_0_axis = plt.Subplot(fig, raster_plot_1_0_gsp[1])
fef_1_0_axis = plt.Subplot(fig, raster_plot_1_0_gsp[2])
v1_1_9_axis = plt.Subplot(fig, raster_plot_1_9_gsp[0])
v2_1_9_axis = plt.Subplot(fig, raster_plot_1_9_gsp[1])
fef_1_9_axis = plt.Subplot(fig, raster_plot_1_9_gsp[2])

# Create axes within violin plot gridspec
rate_1_0_violin_axis = plt.Subplot(fig, violin_plot_1_0_gsp[0])
corr_coeff_1_0_violin_axis = plt.Subplot(fig, violin_plot_1_0_gsp[1])
irregularity_1_0_violin_axis = plt.Subplot(fig, violin_plot_1_0_gsp[2])
rate_1_9_violin_axis = plt.Subplot(fig, violin_plot_1_9_gsp[0])
corr_coeff_1_9_violin_axis = plt.Subplot(fig, violin_plot_1_9_gsp[1])
irregularity_1_9_violin_axis = plt.Subplot(fig, violin_plot_1_9_gsp[2])

# Add axes
fig.add_subplot(v1_1_0_axis)
fig.add_subplot(v2_1_0_axis)
fig.add_subplot(fef_1_0_axis)
fig.add_subplot(v1_1_9_axis)
fig.add_subplot(v2_1_9_axis)
fig.add_subplot(fef_1_9_axis)
fig.add_subplot(rate_1_0_violin_axis)
fig.add_subplot(corr_coeff_1_0_violin_axis)
fig.add_subplot(irregularity_1_0_violin_axis)
fig.add_subplot(rate_1_9_violin_axis)
fig.add_subplot(corr_coeff_1_9_violin_axis)
fig.add_subplot(irregularity_1_9_violin_axis)

# Plot example GeNN raster plots
excitatory_actor, inhibitory_actor = plot_area("V1", v1_1_0_axis, "chi_1_0")
plot_area("V2", v2_1_0_axis, "chi_1_0")
plot_area("FEF", fef_1_0_axis, "chi_1_0")
plot_area("V1", v1_1_9_axis, "chi_1_9")
plot_area("V2", v2_1_9_axis, "chi_1_9")
plot_area("FEF", fef_1_9_axis, "chi_1_9")

vertical = True 

# Combine GeNN and NEST rates and plot split violin plot
plot_violin(nest_rates_1_0, genn_rates_1_0, rate_1_0_violin_axis, 
            vertical, "Rate [spikes/s]", (-1.0, 13.0))
plot_violin(nest_rates_1_9, genn_rates_1_9, rate_1_9_violin_axis, 
            vertical, "Rate [spikes/s]", (-10.0, 150.0))
            
# Combine GeNN and NEST correlation coefficients and plot split violin plot
plot_violin(nest_corr_coeff_1_0, genn_corr_coeff_1_0, corr_coeff_1_0_violin_axis, 
            vertical, "Correlation coefficient", (-0.002, 0.012))
plot_violin(nest_corr_coeff_1_9, genn_corr_coeff_1_9, corr_coeff_1_9_violin_axis, 
            vertical, "Correlation coefficient", (-0.1, 0.6))

# Combine GeNN and NEST irregularity and plot split violin plot
plot_violin(nest_irregularity_1_0, genn_irregularity_1_0, irregularity_1_0_violin_axis, 
            vertical, "Irregularity", (-0.01, 2.01))
plot_violin(nest_irregularity_1_9, genn_irregularity_1_9, irregularity_1_9_violin_axis, 
            vertical, "Irregularity", (-0.5, 2.5))

# Label axes
v1_1_0_axis.set_title("A: V1", loc="left")
v2_1_0_axis.set_title("B: V2", loc="left")
fef_1_0_axis.set_title("C: FEF", loc="left")
v1_1_9_axis.set_title("G: V1", loc="left")
v2_1_9_axis.set_title("H: V2", loc="left")
fef_1_9_axis.set_title("I: FEF", loc="left")


rate_1_0_violin_axis.set_title("D", loc="left")
corr_coeff_1_0_violin_axis.set_title("E", loc="left")
irregularity_1_0_violin_axis.set_title("F", loc="left")
rate_1_9_violin_axis.set_title("J", loc="left")
corr_coeff_1_9_violin_axis.set_title("K", loc="left")
irregularity_1_9_violin_axis.set_title("L", loc="left")

# Configure axis ticks
rate_1_0_violin_axis.yaxis.set_minor_locator(MultipleLocator(5.0))
corr_coeff_1_0_violin_axis.yaxis.set_minor_locator(MultipleLocator(0.005))
irregularity_1_0_violin_axis.yaxis.set_minor_locator(MultipleLocator(1.0))
rate_1_9_violin_axis.yaxis.set_minor_locator(MultipleLocator(100.0))
corr_coeff_1_9_violin_axis.yaxis.set_minor_locator(MultipleLocator(0.25))
irregularity_1_9_violin_axis.yaxis.set_minor_locator(MultipleLocator(1.0))


# Show figure legend with devices beneath figure
pal = sns.color_palette()
fig.legend([Rectangle((0, 0), 1, 1, fc=pal[0]), Rectangle((0, 0), 1, 1, fc=pal[1])],
           ["NEST", "GeNN"], ncol=2, frameon=False, bbox_to_anchor=(0.875, 0.0), loc="lower center")

# Increase size of markers in spike actors
excitatory_actor.set_sizes([10])
inhibitory_actor.set_sizes([10])

# Show second figure legend with inhibitory and excitatory spikes
fig.legend([excitatory_actor, inhibitory_actor],
           ["Excitatory", "Inhibitory"], ncol=2, frameon=False, bbox_to_anchor=(0.333, 0.0), loc="lower center")


fig.align_ylabels([rate_1_0_violin_axis, corr_coeff_1_0_violin_axis, irregularity_1_0_violin_axis,
                   rate_1_9_violin_axis, corr_coeff_1_9_violin_axis, irregularity_1_9_violin_axis])
fig.tight_layout(pad=0, w_pad=2.0, rect= [0.0, 0.035, 1.0, 1.0])

if not plot_settings.presentation:
    fig.savefig("../figures/multi_area.pdf", dpi=600)
    
# Show plot
plt.show()
