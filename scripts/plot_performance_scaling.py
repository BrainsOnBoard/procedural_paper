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
algorithms = ["Sparse", "Bitmask", "Procedural"]

# Import data
# **NOTE** np.loadtxt doesn't handle empty entries
data = np.genfromtxt("scaling_data.csv", delimiter=",", skip_header=1)
assert data.shape[1] == (2 + (len(devices) * len(algorithms)))

def plot_line(data, devices, algorithms, pal):
    fig, axis = plt.subplots(figsize=plot_settings.small_figure)

    line_styles = ["-", "--", ":"]
    assert len(line_styles) == len(algorithms)

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

        # Loop through groups of best algorithms
        index = 0
        for i, (a, group) in enumerate(groupby(device_best_algorithm)):
            group_size = len(list(group))
            axis.plot(data[index:index + group_size + 1,0], device_best[index:index + group_size + 1],
                    color=pal[d], linestyle=line_styles[a])
            index += group_size


    axis.set_xlabel("Number of neurons")
    axis.set_ylabel("Simulation time [s]")
    axis.set_xscale("log")
    axis.set_yscale("log")

    sns.despine(ax=axis)
    legend_actors = []
    legend_text = []
    legend_actors.extend(Rectangle((0, 0), 1, 1, fc=pal[i]) for i, _ in enumerate(devices))
    legend_text.extend(d for d in devices)
    legend_actors.extend(Line2D([], [], linestyle=l) for l in line_styles)
    legend_text.extend(a for a in algorithms)

    fig.legend(flip(legend_actors, 4), flip(legend_text, 4),
            ncol=max(len(devices), len(algorithms)),
            frameon=False, loc="lower center")

    plt.tight_layout(pad=0, rect= [0.0, 0.2, 1.0, 1.0])
    if not plot_settings.presentation:
        fig.savefig("../figures/performance_scaling.pdf")

def plot_bars(data, devices, algorithms, pal):
    fig, axis = plt.subplots(figsize=plot_settings.small_figure)

    hatch_patterns = [None, "....", "////"]
    assert len(hatch_patterns) == len(algorithms)

    time_rows = [0, 2, 4, 6]

    group_size = len(devices) * len(algorithms)
    num_groups = len(time_rows)
    num_bars = group_size * num_groups
    bar_x = np.empty(num_bars)
    bar_height = np.empty(num_bars)

    # Calculate bar positions of grouped GPU bars
    bar_pad = 0.1
    group_pad = 2.0
    bar_width = 0.8

    group_width = ((bar_width + bar_pad) * group_size) + group_pad
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
            bar_start_x = (d * len(algorithms)) + a
            bar_x = np.arange(bar_start_x, bar_start_x + (group_width * num_groups), group_width)

            # Plot bars
            axis.bar(bar_x, device_data[time_rows, a], color=pal[d], hatch=hatch_patterns[a])

    axis.set_xticks(group_x)
    axis.set_xticklabels(data[time_rows,0], ha="center")
    axis.set_yscale("log")
    axis.set_xlabel("Number of neurons")
    axis.set_ylabel("Simulation time [s]")

    sns.despine(ax=axis)

    # Remove vertical grid
    axis.xaxis.grid(False)

    legend_actors = []
    legend_text = []
    legend_actors.extend(Rectangle((0, 0), 1, 1, fc=pal[i]) for i, _ in enumerate(devices))
    legend_text.extend(d for d in devices)
    legend_actors.extend(Rectangle((0, 0), 1, 1, hatch=h) for h in hatch_patterns)
    legend_text.extend(a for a in algorithms)

    fig.legend(flip(legend_actors, 4), flip(legend_text, 4),
            ncol=max(len(devices), len(algorithms)),
            frameon=False, loc="lower center")

    plt.tight_layout(pad=0, rect= [0.0, 0.2, 1.0, 1.0])
    if not plot_settings.presentation:
        fig.savefig("../figures/performance_scaling_bars.pdf")

pal = sns.color_palette("deep")
plot_line(data, devices, algorithms, pal)
plot_bars(data, devices, algorithms, pal)
plt.show()
