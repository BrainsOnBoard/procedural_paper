import numpy as np

# Load voltages
voltages_sparse = np.fromfile("voltages_post.bin", dtype=np.float32)
voltages_proc = np.fromfile("voltages_proc.bin", dtype=np.float32)

# Check shapes match
assert(voltages_sparse.shape == voltages_proc.shape)

num_timesteps = voltages_sparse.shape[0] // 8000
print("%u timesteps" % num_timesteps)

# Convert to double to improve error calculation accuracy
voltages_sparse = voltages_sparse.astype(np.float64)
voltages_proc = voltages_proc.astype(np.float64)

# Caculate error
voltage_err = voltages_sparse - voltages_proc
voltage_err = np.sqrt(np.sum(voltage_err * voltage_err) / len(voltages_sparse))

print("RMSE:%f" % voltage_err)

# Load spikes
spikes_post = np.loadtxt("spikes_post.csv", delimiter=",", skiprows=1,
                         dtype={"names": ("time", "neuron_id"),
                                "formats": (np.float, np.int)})
spikes_proc = np.loadtxt("spikes_proc.csv", delimiter=",", skiprows=1,
                         dtype={"names": ("time", "neuron_id"),
                                "formats": (np.float, np.int)})

assert len(spikes_post) == len(spikes_proc)
post_processed = np.zeros(len(spikes_post), dtype=bool)
proc_processed = np.zeros(len(spikes_proc), dtype=bool)

# Loop through timesteps
for t in range(1, num_timesteps + 1):
    # Get masks to access spikes in this timestep
    timestep_spikes_post = (spikes_post["time"] == t)
    timestep_spikes_proc = (spikes_proc["time"] == t)
    
    # Get sorted neuron ids for timestep
    assert timestep_spikes_post.shape == timestep_spikes_proc.shape
    id_post = np.sort(spikes_post["neuron_id"][timestep_spikes_post])
    id_proc = np.sort(spikes_post["neuron_id"][timestep_spikes_proc])
    
    # Assert they match
    assert np.array_equal(id_post, id_proc)
    
    # Check that none of these spikes have already been processed
    assert not np.any(post_processed[timestep_spikes_post])
    assert not np.any(proc_processed[timestep_spikes_proc])
    
    # Set processed flags for these spikes
    post_processed[timestep_spikes_post] = True
    proc_processed[timestep_spikes_proc] = True

# Assert that all spikes have been compared
assert np.all(post_processed)
assert np.all(proc_processed)
print("Spikes equal!")
