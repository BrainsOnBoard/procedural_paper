import numpy as np
import seaborn as sns
from glob import glob
from matplotlib import pyplot as plt
from scipy.stats import entropy
from sys import argv
from os import path
import plot_settings

def remove_junk(axis):
    sns.despine(ax=axis, left=True)
    axis.xaxis.grid(False)
    
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

permutation_names = ["GeNN vs NEST", "GeNN vs GeNN"]

# Population names
populations = ["4E", "4I", "5E", "5I", "6E", "6I", "23E", "23I"]

rate_kl_div = None
corr_coeff_kl_div = None
irregularity_kl_div = None
for i, p in enumerate(permutations):
    per_rate_kl_div = calc_kl_divergence(data_path, p + "_rates", populations)
    per_corr_coeff_kl_div = calc_kl_divergence(data_path, p + "_corr_coeff", populations)
    per_irregularity_kl_div = calc_kl_divergence(data_path, p + "_irregularity", populations)
    
    if i == 0:
        rate_kl_div = per_rate_kl_div
        corr_coeff_kl_div = per_corr_coeff_kl_div
        irregularity_kl_div = per_irregularity_kl_div
    else:
        rate_kl_div = np.vstack((rate_kl_div, per_rate_kl_div))
        corr_coeff_kl_div = np.vstack((corr_coeff_kl_div, per_corr_coeff_kl_div))
        irregularity_kl_div = np.vstack((irregularity_kl_div, per_irregularity_kl_div))


rate_kl_mean = [np.mean(rate_kl_div[:3,:], axis=0), np.mean(rate_kl_div[3:,:], axis=0)]
rate_kl_std = [np.std(rate_kl_div[:3,:], axis=0), np.std(rate_kl_div[3:,:], axis=0)]

corr_coeff_kl_mean = [np.mean(corr_coeff_kl_div[:3,:], axis=0), np.mean(corr_coeff_kl_div[3:,:], axis=0)]
corr_coeff_kl_std = [np.std(corr_coeff_kl_div[:3,:], axis=0), np.std(corr_coeff_kl_div[3:,:], axis=0)]

irregularity_kl_mean = [np.mean(irregularity_kl_div[:3,:], axis=0), np.mean(irregularity_kl_div[3:,:], axis=0)]
irregularity_kl_std = [np.std(irregularity_kl_div[:3,:], axis=0), np.std(irregularity_kl_div[3:,:], axis=0)]

# Create second figure to show KL divergence
kl_fig, kl_axes = plt.subplots(3, frameon=False,
                               figsize=(8.5 * plot_settings.cm_to_inches, 
                                        6.0 * plot_settings.cm_to_inches))

# Position bars
kl_bar_width = 0.8
kl_bar_pad = 0.2
kl_bar_x = np.arange(0.0, len(populations) * (kl_bar_width + kl_bar_pad), kl_bar_width + kl_bar_pad)

# Plot bars
permutation_actors = []

# Draw rate KL-divergence bars
for i, (m, s) in enumerate(zip(rate_kl_mean, rate_kl_std)):
    permutation_actors.append(kl_axes[0].bar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                                              kl_bar_width, yerr=s, linewidth=0)[0])

# Draw correlation coefficient KL-divergence bars
for i, (m, s) in enumerate(zip(corr_coeff_kl_mean, corr_coeff_kl_std)):
    kl_axes[1].bar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                   kl_bar_width, yerr=s, linewidth=0)

# Draw irregularity KL-divergence bars
for i, (m, s) in enumerate(zip(irregularity_kl_mean, irregularity_kl_std)):
    kl_axes[2].bar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                   kl_bar_width, yerr=s, linewidth=0)

# Set axis labels and titles
for axis, title in zip(kl_axes, ["A", "B", "C"]):
    remove_junk(axis)
    axis.set_ylabel("$D_{KL}$")
    axis.set_title(title, loc="left")
    axis.set_xticks((kl_bar_x * 2) + (kl_bar_width * 0.5))
    axis.set_xticklabels(populations, ha="center")

# Fiddle with ticks
kl_axes[0].set_yticks([0, 0.001, 0.002])
kl_axes[1].set_yticks([0, 0.002, 0.004])
kl_axes[2].set_yticks([0, 0.001, 0.002])

kl_fig.legend(permutation_actors, permutation_names,
              ncol=2, loc="lower center")

kl_fig.tight_layout(pad=0, rect=(0, 0.225, 1, 1))
if not plot_settings.presentation:
    kl_fig.savefig("../figures/microcircuit_accuracy_kl.pdf")

# Show plot
plt.show()
