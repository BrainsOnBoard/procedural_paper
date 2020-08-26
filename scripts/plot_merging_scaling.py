import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import plot_settings

NUM_REPEATS = 5
PLOT_STYLE = {"marker": "o", "markersize": 4.0}

def plot_line(axis, data, column):
    column_data = data[:, column]
    
    column_data = np.reshape(column_data, (-1, NUM_REPEATS))
    mean = np.mean(column_data, axis=1)
    std = np.std(column_data, axis=1)
    
    return axis.errorbar(data[0::NUM_REPEATS,0], mean, yerr=std, **PLOT_STYLE)[0]

# Import data
data = np.genfromtxt("merging_data.csv", delimiter=",", skip_header=1)
assert data.shape[1] == 13

fig, axes = plt.subplots(2, 2, sharex="col", frameon=False,
                         figsize=(8.5 * plot_settings.cm_to_inches, 
                                  5.0 * plot_settings.cm_to_inches))

# Plot compile time
compile_time_axis = axes[0,0]
compile_time_axis.set_title("A", loc="left")
latest_actor = plot_line(compile_time_axis, data, 2)
release_actor = plot_line(compile_time_axis, data, 8)
compile_time_axis.set_ylabel("$T_{comp}$ [s]")
compile_time_axis.set_yticks([0, 1000, 2000])
compile_time_axis.xaxis.grid(False)
compile_time_axis.yaxis.grid(False)
sns.despine(ax=compile_time_axis)

# Plot simulation time
sim_time_axis = axes[0,1]
sim_time_axis.set_title("B", loc="left")
plot_line(sim_time_axis, data, 1)
plot_line(sim_time_axis, data, 7)
sim_time_axis.set_ylabel("$T_{neuron}$ [s]")
sim_time_axis.xaxis.grid(False)
sim_time_axis.yaxis.grid(False)
sns.despine(ax=sim_time_axis)

# Plot SOL time
sol_time_axis = axes[1,0]
sol_time_axis.set_title("C", loc="left")
plot_line(sol_time_axis, data, 4)
plot_line(sol_time_axis, data, 10)
sol_time_axis.set_xlabel("$N_{pop}$")
sol_time_axis.set_ylabel("$K_{mem}$ [%]")
sol_time_axis.set_ylim((0, 100))
sol_time_axis.xaxis.grid(False)
sol_time_axis.yaxis.grid(False)
sns.despine(ax=sol_time_axis)

# Plot instruction stall count
stall_count_axis = axes[1,1]
stall_count_axis.set_title("D", loc="left")
plot_line(stall_count_axis, data, 6)
plot_line(stall_count_axis, data, 12)
stall_count_axis.set_xlabel("$N_{pop}$")
stall_count_axis.set_ylabel("$N_{stall}$")
stall_count_axis.xaxis.grid(False)
stall_count_axis.yaxis.grid(False)
stall_count_axis.set_yticks([0, 25, 50])
sns.despine(ax=stall_count_axis)

fig.legend([latest_actor, release_actor], ["Kernel merging", "GeNN 4.1.0"], 
           ncol=2, frameon=False, loc="lower center")
fig.align_ylabels()
fig.tight_layout(pad=0, rect= [0.0, 0.1, 1.0, 1.0])
if not plot_settings.presentation:
    fig.savefig("../figures/merging_scaling.pdf")
plt.show()