import numpy as np
import seaborn as sns
from glob import glob
from matplotlib import pyplot as plt
from scipy.stats import entropy
from sys import argv
from os import path
import plot_settings

def remove_junk(axis):
    sns.despine(ax=axis, left=True, bottom=True)
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

permutations = ["nest_seed_1", "nest_seed_2", "nest_seed_3",
                "seed_1_seed_2", "seed_1_seed_3", "seed_2_seed_3"]

permutation_names = ["GeNN vs NEST", "GeNN vs GeNN"]

# Population names
populations = ["4E", "4I", "5E", "5I", "6E", "6I", "23E", "23I"]

# Create second figure to show KL divergence
kl_fig, kl_axes = plt.subplots(6, frameon=False, sharex=True,
                               figsize=(8.5 * plot_settings.cm_to_inches, 
                                        8.5 * plot_settings.cm_to_inches))

# Position bars
kl_bar_width = 0.8
kl_bar_pad = 0.2
kl_bar_x = np.arange(0.0, len(populations) * (kl_bar_width + kl_bar_pad), kl_bar_width + kl_bar_pad)

# Plot bars
permutation_actors = []

errorbar_kwargs = {"linestyle": "None", "marker": "o", "markersize": 0.5,
                   "capsize": 5.0, "elinewidth": 0.5, "capthick": 0.5}

# Loop through datasets
for j, d in enumerate(["chi_1_0", "chi_1_9"]):
    rate_kl_div = None
    corr_coeff_kl_div = None
    irregularity_kl_div = None
    for i, p in enumerate(permutations):
        per_rate_kl_div = calc_kl_divergence(d, p + "_rates", populations)
        per_corr_coeff_kl_div = calc_kl_divergence(d, p + "_corr_coeff", populations)
        per_irregularity_kl_div = calc_kl_divergence(d, p + "_irregularity", populations)
        
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

    # Draw rate KL-divergence bars
    for i, (m, s) in enumerate(zip(rate_kl_mean, rate_kl_std)):
        permutation_actors.append(kl_axes[(j * 3) + 0].errorbar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                                                                yerr=s, **errorbar_kwargs)[2])

    # Draw correlation coefficient KL-divergence bars
    for i, (m, s) in enumerate(zip(corr_coeff_kl_mean, corr_coeff_kl_std)):
        kl_axes[(j * 3) + 1].errorbar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                                       yerr=s, **errorbar_kwargs)

    # Draw irregularity KL-divergence bars
    for i, (m, s) in enumerate(zip(irregularity_kl_mean, irregularity_kl_std)):
        kl_axes[(j * 3) + 2].errorbar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                                       yerr=s, **errorbar_kwargs)

# Loop through axis grid
for i in range(6):
    remove_junk(kl_axes[i])
    
    kl_axes[i].set_title(chr(ord("A") + i), loc="left")
    
    kl_axes[i].set_ylabel("$D_{KL}$")

    # Configure x axis on bottom row
    if i == 5:
        kl_axes[i].set_xticks((kl_bar_x * 2) + (kl_bar_width * 0.5))
        kl_axes[i].set_xticklabels(populations, ha="center")
        

# Fiddle with ticks
kl_axes[0].set_yticks([0, 0.001, 0.002])
kl_axes[1].set_yticks([0, 0.002, 0.004])
kl_axes[2].set_yticks([0, 0.001, 0.002])
kl_axes[3].set_yticks([0, 0.01, 0.02])
kl_axes[4].set_yticks([0, 0.025, 0.05])
kl_axes[5].set_yticks([0, 0.025, 0.05])

kl_fig.legend(permutation_actors, permutation_names,
              ncol=2, loc="lower center", frameon=False)

kl_fig.tight_layout(pad=0, rect=(0, 0.075, 1, 1))
if not plot_settings.presentation:
    kl_fig.savefig("../figures/microcircuit_accuracy_kl.pdf")

# Show plot
plt.show()
