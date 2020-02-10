import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import seaborn as sns
import plot_settings

from itertools import chain, groupby
from six import iterkeys, itervalues

def flip(items, ncol):
    return chain(*[items[i::ncol] for i in range(ncol)])

devices = ["Jetson TX2", "GeForce MX130", "GeForce GTX 1650", "Titan RTX"]
algorithms = ["Sparse", "Bitmask", "Procedural"]


line_styles = ["-", "--", ":"]

assert len(line_styles) == len(algorithms)

# Import data, leaving special characters alone and not replacing spaces
data = np.genfromtxt("scaling_data.csv", delimiter=",", skip_header=1)
assert data.shape[1] == (2 + (len(devices) * len(algorithms)))

pal = sns.color_palette("deep")

fig, axis = plt.subplots(figsize=plot_settings.small_figure)

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
plt.show()
