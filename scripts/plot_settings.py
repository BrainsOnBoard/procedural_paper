import seaborn as sns
import sys

presentation = "presentation" in sys.argv[1:]

# Set the plotting style
if presentation:
    sns.set(context="talk")
    sns.set_style("whitegrid", {"font.family":"sans-serif", "font.sans-serif":"Verdana"})
else:
    sns.set(context="paper", rc={"font.size":7, "axes.labelsize":7, "axes.titlesize": 8,
                                 "legend.fontsize":7, "xtick.labelsize":7, "ytick.labelsize":7})
    sns.set_style("whitegrid", {"font.family":"serif", "font.serif":"Times New Roman"})

# **HACK** fix bug with markers
sns.set_context(rc={"lines.markeredgewidth": 1.0})



cm_to_inches = 0.39370079
small_figure = (9.0 * cm_to_inches, 6.0 * cm_to_inches)
medium_figure = (11.0 * cm_to_inches, 11.0 * cm_to_inches)
large_figure = (18.0 * cm_to_inches, 22.0 * cm_to_inches)
