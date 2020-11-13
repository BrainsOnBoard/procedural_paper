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

def label_populations(axis, populations, kl_bar_x, kl_bar_width):
    axis.set_xticks((kl_bar_x * 2) + (kl_bar_width * 0.5))
    axis.set_xticklabels(populations, ha="center")

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
kl_fig, kl_axes = plt.subplots(3, 2, frameon=False, sharex="col",
                               figsize=(17.0 * plot_settings.cm_to_inches, 
                                        5 * plot_settings.cm_to_inches))

# Position bars
kl_bar_width = 0.8
kl_bar_pad = 0.2
kl_bar_x = np.arange(0.0, len(populations) * (kl_bar_width + kl_bar_pad), kl_bar_width + kl_bar_pad)

# Plot bars
permutation_actors = []

errorbar_kwargs = {"linestyle": "None", "marker": "o", "markersize": 1.0,
                   "capsize": 5.0, "elinewidth": 0.75, "capthick": 0.75}

# Loop through datasets
max_axis_value = np.empty((3,2))
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
        permutation_actors.append(kl_axes[0, j].errorbar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                                                         yerr=s, **errorbar_kwargs)[2])
                                                         
        max_axis_value[0, j] = np.amax(m + s)

    # Draw correlation coefficient KL-divergence bars
    for i, (m, s) in enumerate(zip(corr_coeff_kl_mean, corr_coeff_kl_std)):
        kl_axes[1, j].errorbar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                               yerr=s, **errorbar_kwargs)
        
        max_axis_value[1, j] = np.amax(m + s)

    # Draw irregularity KL-divergence bars
    for i, (m, s) in enumerate(zip(irregularity_kl_mean, irregularity_kl_std)):
        kl_axes[2, j].errorbar((kl_bar_x * 2.0) + (i * kl_bar_width), m, 
                                       yerr=s, **errorbar_kwargs)
        max_axis_value[2, j] = np.amax(m + s)
        
# Configure x-axis on bottom row
label_populations(kl_axes[2, 0], populations, kl_bar_x, kl_bar_width)
label_populations(kl_axes[2, 1], populations, kl_bar_x, kl_bar_width)

# Fiddle with ticks
kl_axes[0, 0].set_yticks([0, 0.001, 0.002])
kl_axes[1, 0].set_yticks([0, 0.002, 0.004])
kl_axes[2, 0].set_yticks([0, 0.001, 0.002])

kl_axes[0, 1].set_yticks([0, 0.01, 0.02])
kl_axes[1, 1].set_yticks([0, 0.025, 0.05])
kl_axes[2, 1].set_yticks([0, 0.025, 0.05])

# Calculate how much each axis overflows it's grid
axis_grid_overflow = np.empty((3,2))
for i in range(3):
    for j in range(2):
        max_axis_tick = np.amax(kl_axes[i, j].get_yticks())
        axis_grid_overflow[i, j] = (max_axis_value[i, j] - max_axis_tick) / max_axis_tick

# Calculate the maximum overflow for each row (clamping above zero as we want to show at least the grid)
max_grid_row_overflow = np.maximum(0.0, np.amax(axis_grid_overflow, axis=1))

# Loop through axis grid
for i in range(3):
    for j in range(2):
        ax = kl_axes[i, j]
        ax.set_title(chr(ord("A") + (i * 2) + j), loc="left")
        ax.set_ylabel("$D_{KL}$")
        
        # Configure the upper y-axis limit to match the row-wise maximum
        y_ticks = ax.get_yticks()
        ax.set_ylim((np.amin(y_ticks), 
                     np.amax(y_ticks) * (1.0 + max_grid_row_overflow[i])))
        
        remove_junk(ax)


kl_fig.legend(permutation_actors, permutation_names,
              ncol=2, loc="lower center", frameon=False)

kl_fig.tight_layout(pad=0, rect=(0, 0.11, 1, 1))
if not plot_settings.presentation:
    kl_fig.savefig("../figures/microcircuit_accuracy_kl.pdf")

# Show plot
plt.show()
