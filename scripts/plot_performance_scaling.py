import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import plot_settings

from itertools import chain
from six import iterkeys, itervalues

def flip(items, ncol):
    return chain(*[items[i::ncol] for i in range(ncol)])

markers = ["o", "^", "s"]

# Import data, leaving special characters alone and not replacing spaces
data = np.genfromtxt("scaling_data.csv", names=True, delimiter=",", deletechars="", replace_space=None)

pal = sns.color_palette("deep")

fig, axis = plt.subplots(figsize=(plot_settings.large_figure[0], 8.0 * plot_settings.cm_to_inches))

device_colours = {}
connectivity_markers = {}

# Loop through names of columns containing experiment data
for n in data.dtype.names[2:]:
    # Extract device and connectivity name from column name
    device_name, connectivity_name = (f.strip(" ") for f in n.split("-"))

    # Find colour corresponding to device
    if device_name in device_colours:
        colour = device_colours[device_name]
    else:
        colour = pal[len(device_colours)]
        device_colours[device_name] = colour

    # Find marker correspond to connectivity
    if connectivity_name in connectivity_markers:
        marker = connectivity_markers[connectivity_name]
    else:
        marker = markers[len(connectivity_markers)]
        connectivity_markers[connectivity_name] = marker

    # Plot
    axis.plot(data["Num neurons"], data[n], color=colour, marker=marker)

axis.set_xlabel("Number of neurons")
axis.set_ylabel("Simulation time [s]")
axis.set_xscale("log")
axis.set_yscale("log")

sns.despine(ax=axis)
legend_actors = []
legend_text = []
legend_actors.extend(Line2D([], [], color=c) for c in itervalues(device_colours))
legend_text.extend(d for d in iterkeys(device_colours))
legend_actors.extend(Line2D([], [], marker=m, linestyle="none") for m in itervalues(connectivity_markers))
legend_text.extend(c for c in iterkeys(connectivity_markers))

fig.legend(flip(legend_actors, 4), flip(legend_text, 4),
           ncol=max(len(device_colours), len(connectivity_markers)),
           frameon=False, loc="lower center")

plt.tight_layout(pad=0, rect= [0.0, 0.175, 1.0, 1.0])
if not plot_settings.presentation:
    fig.savefig("../figures/performance_scaling.pdf")
plt.show()
