from glob import glob
import numpy as np
from sys import argv
from os import path
from scipy.stats import iqr

if __name__ == '__main__':
    assert len(argv) >= 4
    data_path = argv[1]
    ground_truth_folder = argv[2]
    comparison_folder = argv[3]

    # Loop through numpy files in ground truth path
    for s in glob(path.join(data_path, ground_truth_folder, "*.npy")):
        # Get name
        name = path.basename(s)
        print(name)

        # Get path to corresponding file in comparison path
        comparison_path = path.join(data_path, comparison_folder, name)
        if path.exists(comparison_path):
            # Load both data files
            ground_truth_data = np.load(s)
            comparison_data = np.load(comparison_path)

            # Calculate bin-size using Freedman-Diaconis rule
            bin_size = (2.0 * iqr(ground_truth_data)) / (float(len(ground_truth_data)) ** (1.0 / 3.0))

            # Thus determine bins
            min_y = np.amin(ground_truth_data)
            max_y = np.amax(ground_truth_data)
            num_bins = int(np.ceil((max_y - min_y) / bin_size))
            bin_x = np.linspace(min_y, max_y, num_bins)

            # Calculate histograms
            ground_truth_hist,_ = np.histogram(ground_truth_data, bins=bin_x)
            comparison_hist,_ = np.histogram(comparison_data, bins=bin_x)
 
            # Write bins and histograms to disk
            with open(ground_truth_folder + "_" + comparison_folder + "_" + name, "wb") as f:
                np.save(f, bin_x)
                np.save(f, ground_truth_hist)
                np.save(f, comparison_hist)
        else:
            print("WARNING: Unable to find file to compare %s against" % name)
