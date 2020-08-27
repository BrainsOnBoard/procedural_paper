import numpy as np
from glob import glob
from matplotlib import pyplot as plt
from scipy.stats import entropy
from sys import argv
from os import path
import plot_settings

def calc_kl_divergence(data_path, prefix, populations):
    # Loop through populations
    kls = []
    for p in populations:
        with open(path.join(data_path, prefix + "_" + p + ".npy"), "rb") as f:
            bin_x = np.load(f)
            ground_truth_hist = np.load(f)
            comp_hist = np.load(f)

        # Normalize histograms
        bin_width = bin_x[1] - bin_x[0]
        ground_truth_hist = np.divide(ground_truth_hist, np.sum(ground_truth_hist) / bin_width, dtype="float")
        comp_hist = np.divide(comp_hist, np.sum(comp_hist) / bin_width, dtype="float")
        
        # Mask out bins with no data
        mask = (comp_hist > 1.0E-15)
        kls.append(entropy(ground_truth_hist[mask], comp_hist[mask]))
    
    # Return KL divergences as array
    return np.asarray(kls)

assert len(argv) >= 2
data_path = argv[1]

permutations = ["nest_seed_1", "nest_seed_2", "nest_seed_3",
                "seed_1_seed_2", "seed_1_seed_3", "seed_2_seed_3"]

# Population names
populations = ["4E", "4I", "5E", "5I", "6E", "6I", "23E", "23I"]

rate_kl_div = []
corr_coeff_kl_div = []
irregularity_div = []
for p in permutations:
    rate_kl_div.append(calc_kl_divergence(data_path, p + "_rates", populations))
    corr_coeff_kl_div.append(calc_kl_divergence(data_path, p + "_corr_coeff", populations))
    irregularity_div.append(calc_kl_divergence(data_path, p + "_irregularity", populations))

# Create second figure to show KL divergence
kl_fig, kl_axes = plt.subplots(3, frameon=False,
                               figsize=(8.5 * plot_settings.cm_to_inches, 
                                        5.0 * plot_settings.cm_to_inches))

# Position bars
kl_bar_width = 0.8
kl_bar_pad = 0.4
kl_bar_x = np.arange(0.0, len(populations) * (kl_bar_width + kl_bar_pad), kl_bar_width + kl_bar_pad)

# Plot bars
permutation_actors = []

for i, r in enumerate(rate_kl_div):
    permutation_actors.append(kl_axes[0].bar((kl_bar_x * len(permutations)) + (i * kl_bar_width), r, kl_bar_width)[0])
    
for i, c in enumerate(corr_coeff_kl_div):
    kl_axes[1].bar((kl_bar_x * len(permutations)) + (i * kl_bar_width), c, kl_bar_width)

for i, g in enumerate(irregularity_div):
    kl_axes[2].bar((kl_bar_x * len(permutations)) + (i * kl_bar_width), g, kl_bar_width)

# Set axis labels and titles
for axis, title in zip(kl_axes, ["A", "B", "C"]):
    axis.set_ylabel("$D_{KL}$")
    axis.set_title(title, loc="left")
    axis.set_xticks(kl_bar_x * len(permutations))
    axis.set_xticklabels(populations, ha="center")

kl_fig.legend(permutation_actors, permutations,
              ncol=3, loc="lower center")

#kl_fig.tight_layout(pad=0, rect=(0, 0.15, 1, 1))
#kl_fig.savefig("../figures/microcircuit_accuracy_kl.eps")

# Show plot
plt.show()
