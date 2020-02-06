import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import plot_settings

markers = ["o", "^", "s"]

# Import data, leaving special characters alone and not replacing spaces
data = np.genfromtxt("scaling_data.csv", names=True, delimiter=",", deletechars="", replace_space=None)

pal = sns.color_palette("deep")

fig, axis = plt.subplots(figsize=plot_settings.small_figure)

device_colours = {}
connectivity_markers = {}

# Loop through names of columns containing experiment data
for n in data.dtype.names[2:]:
    device_name, connectivity_name = (f.strip(" ") for f in n.split("-"))

    if device_name in device_colours:
        colour = device_colours[device_name]
    else:
        colour = pal[len(device_colours)]
        device_colours[device_name] = colour

    if connectivity_name in connectivity_markers:
        marker = connectivity_markers[connectivity_name]
    else:
        marker = markers[len(connectivity_markers)]
        connectivity_markers[connectivity_name] = marker

    axis.plot(data["Num neurons"], data[n], color=colour, marker=marker)

axis.set_xlabel("Number of neurons")
axis.set_ylabel("Simulation time [s]")
axis.set_xscale("log")
axis.set_yscale("log")
plt.tight_layout(pad=0)
plt.show()
