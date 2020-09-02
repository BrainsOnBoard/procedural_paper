import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import LogFormatterExponent
import seaborn as sns
import plot_settings

from itertools import chain, groupby
from six import iterkeys, itervalues

# Names and algorithms - could extract them from CSV but it's a ball-ache
devices = ["Jetson TX2", "GeForce MX130", "GeForce GTX 1650", "Titan RTX"]
algorithms = ["Sparse", "Bitfield", "Procedural"]

# Import data
# **NOTE** np.loadtxt doesn't handle empty entries
data = np.genfromtxt("scaling_data.csv", delimiter=",", skip_header=1)
assert data.shape[1] == (2 + (5 * len(devices) * len(algorithms)))

def plot_line(axis, data, device_index, algorithms, pal, show_y_axis_label=True):
    num_repeats = 5

    # Extract the chunk of data associated with this device
    start_col = 2 + (len(algorithms) * device_index * num_repeats)
    end_col = start_col + (len(algorithms) * num_repeats)
    device_data = data[:,start_col:end_col]

    # Check shape is as expected
    assert device_data.shape[1] == (len(algorithms) * num_repeats)
    
    # Loop through algorithms
    for i, a in enumerate(algorithms):
        # Extract the chunk of data associated with this algorithm
        start_col = i * num_repeats
        end_col = start_col + num_repeats
        algorithm_data = device_data[:,start_col:end_col]
        
        # Check shape is as expected
        assert algorithm_data.shape[1] == num_repeats
        
        # Build mask of rows containing all valid data
        valid_data = np.logical_not(np.any(np.isnan(algorithm_data), axis=1))
        
        # Calculate mean of valid data
        mean_time = np.mean(algorithm_data[valid_data,:], axis=1)
        
        # Calculate standard deviations of valid data
        std = np.std(algorithm_data[valid_data,:], axis=1)
        
        # Extract matching subset of neuron counts
        num_neurons = data[valid_data,0]
        
        # Plot
        axis.errorbar(num_neurons, mean_time, yerr=std, marker="o", markersize=4.0)

    # Configure axis
    axis.set_xlabel("Number of neurons")
    if show_y_axis_label:
        axis.set_ylabel("Simulation time [s]")
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_yticks([1E-3, 1E0, 1E3])
    
    # Remove axis junk
    sns.despine(ax=axis)

pal = sns.color_palette()
fig, axes = plt.subplots(1, len(devices), sharey=True, 
                         figsize=(17.0 * plot_settings.cm_to_inches, 
                                  5.0 * plot_settings.cm_to_inches))

# Plot data for each device
for i, a in enumerate(axes):
    plot_line(a, data, i, algorithms, pal, i == 0)

# Add axis labels
for i, a in enumerate(axes):
    a.set_title(chr(ord("A") + i), loc="left")

# Show figure legend with devices beneath figure
legend_actors = [Line2D([], [], color=p) for _, p in zip(algorithms, pal)]
fig.legend(legend_actors, algorithms, ncol=len(algorithms), frameon=False, loc="lower center")

plt.tight_layout(pad=0, w_pad=1.0, rect= [0.0, 0.125, 1.0, 1.0])
if not plot_settings.presentation:
    fig.savefig("../figures/performance_scaling.pdf")
plt.show()
