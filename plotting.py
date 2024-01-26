# This should be agnostic to the data source (should plot depending on the type of data and series provided)
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

from dataprep import get_exercise_series, get_powerlifting_series

# TODO: improve specs for functions

# Setup plot style

sns.set_style("darkgrid")
plt.rc("axes", labelsize=14)  # fontsize of the x and y labels
plt.rc("font", size=12)  # controls default text sizes
COLOR_PALETTE = np.array(sns.color_palette(palette="Accent"))
COLOR_PALETTE[:5, :] = COLOR_PALETTE[[4, 6, 2, 1, 0], :]


def line_plot(ax, xs, ys, plot_multiple, palette, series_labels=None):
    if plot_multiple:
        for series in ys:
            ax.plot(
                xs,
                series,
                color=next(palette),
                label=next(series_labels),
            )
        ax.legend(loc="upper right")
    else:
        ax.plot(xs, ys[0], color=next(palette))


def plot_multiple(ax, series, labels_iter):
    palette = iter(COLOR_PALETTE)
    top = -1
    for x_series, y_series in series:
        top = max(max(y_series), top)
        ax.scatter(x_series, y_series, color=next(palette), label=next(labels_iter))
    ax.legend(loc="upper right")
    ax.set_ylim(bottom=0, top=top * 1.5)


# fig, ax = plt.subplots()
# a_type = "orm"
# indices = [1, 5, 16, 10]
# series = [get_exercise_series(i, agg_type=a_type) for i in indices]
# series_labels = iter(["deadlifts", "bench press", "squats", "cable rows"])

# plot_multiple(ax, series, series_labels)
# plt.show()

fig, ax = plt.subplots()
series = get_powerlifting_series(agg_type="proportions")
series_labels = iter(["deadlifts", "bench press", "squats"])

# series = get_powerlifting_series(agg_type="wilkes")
# series_labels = iter(["total"])

plot_multiple(ax, series, series_labels)
plt.show()
