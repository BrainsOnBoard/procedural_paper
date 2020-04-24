from glob import glob
from itertools import repeat
from matplotlib import gridspec as gs
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
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
    sns.despine(ax=axis, left=True, bottom=True)
    axis.xaxis.grid(False)

def load_pop_data(stat_file_stem, simulator_prefix):
    # Create default dict for data
    populations = []
    values = []
    
    # Get list of files containing data for this
    data_files = list(glob("%s_%s_*.npy" % (simulator_prefix, stat_file_stem)))
    
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
                     rasterized=True, edgecolors="none", 
                     color="firebrick" if is_inhibitory else "navy")

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
nest_rates = load_pop_data("rates", "nest")
nest_irregularity = load_pop_data("irregularity", "nest")
nest_corr_coeff = load_pop_data("corr_coeff", "nest")

# Load pre-processed GeNN data
genn_rates = load_pop_data("rates", "genn")
genn_irregularity = load_pop_data("irregularity", "genn")
genn_corr_coeff = load_pop_data("corr_coeff", "genn")

# Create plot
fig = plt.figure(frameon=False, figsize=(17.0 * plot_settings.cm_to_inches, 
                                         9.0 * plot_settings.cm_to_inches))

# Create outer gridspec dividing plot area into 3 (2/3 for raster plots, 1/3 for violin plots)
gsp = gs.GridSpec(1, 3)

# Create sub-gridspecs for panels within outer gridspec
violin_plot_gsp = gs.GridSpecFromSubplotSpec(3, 1, subplot_spec=gsp[2], hspace=0.9)
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
            vertical, "Rate [spikes/s]", (-1.0, 13.0))

# Combine GeNN and NEST correlation coefficients and plot split violin plot
plot_violin(nest_corr_coeff, genn_corr_coeff, corr_coeff_violin_axis, 
            vertical, "Correlation coefficient", (-0.002, 0.012))

# Combine GeNN and NEST irregularity and plot split violin plot
plot_violin(nest_irregularity, genn_irregularity, irregularity_violin_axis, 
            vertical, "Irregularity", (-0.01, 2.01))

# Label axes
v1_axis.set_title("A: V1", loc="left")
v2_axis.set_title("B: V2", loc="left")
fef_axis.set_title("C: FEF", loc="left")
rate_violin_axis.set_title("D", loc="left")
corr_coeff_violin_axis.set_title("E", loc="left")
irregularity_violin_axis.set_title("F", loc="left")

rate_violin_axis.yaxis.set_minor_locator(MultipleLocator(5.0))
corr_coeff_violin_axis.yaxis.set_minor_locator(MultipleLocator(0.005))
irregularity_violin_axis.yaxis.set_minor_locator(MultipleLocator(1.0))

# Show figure legend with devices beneath figure
pal = sns.color_palette()
fig.legend([Rectangle((0, 0), 1, 1, fc=pal[0]), Rectangle((0, 0), 1, 1, fc=pal[1])],
           ["NEST", "GeNN"], ncol=2, frameon=False, bbox_to_anchor=(0.875, 0.0), loc="lower center")
fig.align_ylabels([rate_violin_axis, corr_coeff_violin_axis, irregularity_violin_axis])
fig.tight_layout(pad=0, w_pad=2.0, rect= [0.0, 0.075, 1.0, 1.0])

if not plot_settings.presentation:
    fig.savefig("../figures/multi_area.pdf", dpi=600)
    
# Show plot
plt.show()
