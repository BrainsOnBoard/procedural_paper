import csv
import matplotlib.pyplot as plt
import numpy as np


# Read CSV spikes
spikes = np.loadtxt("spikes.csv", delimiter=",", skiprows=1,
                    dtype={"names": ("time", "neuron_id"),
                           "formats": (np.float, np.int)})

# Create plot
figure, axes = plt.subplots(2, sharex=True)

# Plot spikes
axes[0].scatter(spikes["time"], spikes["neuron_id"], s=2, edgecolors="none")

# Plot rates
bins = np.arange(0, 10000 + 1, 10)
rate = np.histogram(spikes["time"], bins=bins)[0] *  (1000.0 / 10.0) * (1.0 / 3200.0)
axes[1].plot(bins[0:-1], rate)

axes[0].set_title("Spikes")
axes[1].set_title("Firing rates")

axes[0].set_xlim((0, 10000))
axes[0].set_ylim((0, 3200))

axes[0].set_ylabel("Neuron number")
axes[1].set_ylabel("Mean firing rate [Hz]")

axes[1].set_xlabel("Time [ms]")

# Show plot
plt.show()

