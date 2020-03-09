import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import plot_settings

# Import data
data = np.genfromtxt("merging_data.csv", delimiter=",", skip_header=1)
assert data.shape[1] == 11

fig, axes = plt.subplots(2, 2, sharex="col", figsize=plot_settings.medium_figure)

# Plot compile time
axes[0,0].set_title("A", loc="left")
latest_actor = axes[0,0].plot(data[:,0], data[:,2])[0]
release_actor = axes[0,0].plot(data[:,0], data[:,7])[0]
axes[0,0].set_ylabel("Compilation time [s]")
sns.despine(ax=axes[0,0])
#axis.xaxis.grid(False)

# Plot simulation time
axes[0,1].set_title("B", loc="left")
axes[0,1].plot(data[:,0], data[:,1])
axes[0,1].plot(data[:,0], data[:,6])
axes[0,1].set_ylabel("Simulation time [s]")
sns.despine(ax=axes[0,1])

# Plot SOL time
axes[1,0].set_title("C", loc="left")
axes[1,0].plot(data[:,0], data[:,3])
#axes[1,0].plot(data[:,0], data[:,4], color=pal[0], linestyle="--")
axes[1,0].plot(data[:,0], data[:,8])
#[1,0].plot(data[:,0], data[:,9], color=pal[1], linestyle="--")
axes[1,0].set_xlabel("Num populations")
axes[1,0].set_ylabel("Memory 'speed of light' [%]")
axes[1,0].set_ylim((0, 100))
sns.despine(ax=axes[1,0])

# Plot instruction stall count
axes[1,1].set_title("D", loc="left")
axes[1,1].plot(data[:,0], data[:,5])
axes[1,1].plot(data[:,0], data[:,10])
axes[1,1].set_xlabel("Num populations")
axes[1,1].set_ylabel("Instruction stall count")
sns.despine(ax=axes[1,1])

fig.legend([latest_actor, release_actor], ["Latest version", "GeNN 4.1.0"], 
           ncol=2, frameon=False, loc="lower center")

plt.tight_layout(pad=0, rect= [0.0, 0.1, 1.0, 1.0])
if not plot_settings.presentation:
    fig.savefig("../figures/merging_scaling.pdf")
plt.show()