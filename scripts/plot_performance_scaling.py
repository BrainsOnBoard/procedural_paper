import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import LogFormatterExponent
import seaborn as sns
import plot_settings

from itertools import chain, groupby
from six import iterkeys, itervalues

def flip(items, ncol):
    return chain(*[items[i::ncol] for i in range(ncol)])

# Names and algorithms - could extract them from CSV but it's a ball-ache
devices = ["Jetson TX2", "GeForce MX130", "GeForce GTX 1650", "Titan RTX"]
algorithms = ["Sparse", "Bitfield", "Procedural"]

# Import data
# **NOTE** np.loadtxt doesn't handle empty entries
data = np.genfromtxt("scaling_data.csv", delimiter=",", skip_header=1)
assert data.shape[1] == (2 + (len(devices) * len(algorithms)))

def plot_line(axis, data, devices, algorithms, pal, show_y_axis_label=True):
    markers = ["o", "D", "s"]
    assert len(markers) == len(algorithms)

    # Loop through devices
    for d, _ in enumerate(devices):
        # Extract the chunk of data associated with this device
        start_col = 2 + (len(algorithms) * d)
        end_col = start_col + len(algorithms)
        device_data = data[:,start_col:end_col]

        # Check shape is as expected
        assert device_data.shape[1] == len(algorithms)

        # Find best algorithms at each point
        device_best_algorithm = np.nanargmin(device_data, axis=1)
        device_best = np.nanmin(device_data, axis=1)

        # Plot line through best data points
        axis.plot(data[:,0], device_best[:], color=pal[d])

        # Loop through groups of best algorithms
        index = 0
        for i, (a, group) in enumerate(groupby(device_best_algorithm)):
            group_size = len(list(group))
            axis.scatter(data[index:index + group_size,0], device_best[index:index + group_size],
                         color=pal[d], marker=markers[a], s=15.0)
            index += group_size

    # Configure axis
    axis.set_xlabel("Number of neurons")
    if show_y_axis_label:
        axis.set_ylabel("Simulation time [s]")
    axis.set_xscale("log")
    axis.set_yscale("log")

    # Remove axis junk
    sns.despine(ax=axis)

    # Add axis legend
    legend_actors = [Line2D([], [], marker=m) for m in markers]
    axis.legend(legend_actors, algorithms, frameon=False, loc="upper left")


def plot_bars(axis, data, devices, algorithms, pal, show_y_axis_label=True):
    alphas = [0.0, 0.5, 1.0]
    assert len(alphas) == len(algorithms)

    time_rows = [0, 2, 4, 6]

    group_size = len(devices) * len(algorithms)
    num_groups = len(time_rows)
    num_bars = group_size * num_groups
    bar_x = np.empty(num_bars)
    bar_height = np.empty(num_bars)

    bar_width = 0.8
    group_width = 15.0
    group_x = np.arange(group_width * 0.5, group_width * (num_groups - 0.5), group_width)

    # Loop through devices
    for d, _ in enumerate(devices):
        # Extract the chunk of data associated with this device
        start_col = 2 + (len(algorithms) * d)
        end_col = start_col + len(algorithms)
        device_data = data[:,start_col:end_col]

        # Check shape is as expected
        assert device_data.shape[1] == len(algorithms)

        # Loop through algorithms
        for a, _ in enumerate(algorithms):
            # Calculate bar positions
            bar_x = [(group_width * i) + (3.5 * d) + a
                     for i in range(num_groups)]
            
            # Plot bars
            axis.bar(bar_x, device_data[time_rows, a], width=bar_width, linewidth=0.3,
                     color=(pal[d][0], pal[d][1], pal[d][2], alphas[a]), ec=(0.0, 0.0, 0.0, 1.0))

    # Configure axis
    axis.set_xticks(group_x)
    axis.set_xticklabels(["$10^{%u}$" % np.log10(d) for d in data[time_rows,0]], ha="center")
    axis.set_yscale("log")
    axis.set_xlabel("Number of neurons")
    if show_y_axis_label:
        axis.set_ylabel("Simulation time [s]")

    # Remove axis junk
    sns.despine(ax=axis)
    axis.xaxis.grid(False)

    # Add axis legend
    legend_actors = [Rectangle((0, 0), 1, 1, fc=(0.0, 0.0, 0.0, a), ec=(0.0, 0.0, 0.0, 1.0)) for a in alphas]
    axis.legend(legend_actors, algorithms, frameon=False, loc="upper left")

pal = sns.color_palette("deep")
fig, axes = plt.subplots(1, 2, sharey=True, figsize=(plot_settings.large_figure[0], plot_settings.small_figure[1]))
plot_line(axes[0], data, devices, algorithms, pal)
plot_bars(axes[1], data, devices, algorithms, pal, False)

axes[0].set_title("A", loc="left")
axes[1].set_title("B", loc="left")
# Show figure legend with devices beneath figure
legend_actors = [Rectangle((0, 0), 1, 1, fc=pal[i]) for i, _ in enumerate(devices)]
fig.legend(legend_actors, devices, ncol=len(devices), frameon=False, loc="lower center")

plt.tight_layout(pad=0, rect= [0.0, 0.15, 1.0, 1.0])
if not plot_settings.presentation:
    fig.savefig("../figures/performance_scaling.pdf")
plt.show()
