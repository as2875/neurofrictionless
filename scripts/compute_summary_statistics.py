# -*- coding: utf-8 -*-

import datapackage
import datetime
import os
import statistics
import elephant.statistics
import h5fd.plot
from h5fd.plot import RECORDING_ATTEMPTS
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import quantities as qt
from tqdm import tqdm

# adjust matplotlib parameters
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [3.35, 7.5]
matplotlib.rcParams["figure.constrained_layout.use"] = True
matplotlib.rcParams["lines.markersize"] = 3.0
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_FILE = "../plots/development_plots.pdf"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

age_l, age_perchan_l, fr_l, active_channels_l, fr_perchan_l, \
    colours, colours_perchan = ({"2539": [], "2540": []} for i in range(7))
fr_errors = {"2539": [[], []], "2540": [[], []]}
for file in tqdm(data_files):
    # load package
    package = datapackage.Package(file)
    mea = package.descriptor["meta"]["MEA"]

    # spike times
    spikes, channels, t_stop = h5fd.plot.extract_spike_trains(package,
                                                              qt.ms,
                                                              qt.s)

    age = package.descriptor["meta"]["age"]
    age_l[mea].append(age)
    
    datestamp = package.descriptor["meta"]["date"]
    recording_date = datetime.date(int("20" + datestamp[:2]),
                                   int(datestamp[2:4]),
                                   int(datestamp[4:]))
    if RECORDING_ATTEMPTS[0][0] <= recording_date <= RECORDING_ATTEMPTS[0][1]:
        colour = "r"
    elif RECORDING_ATTEMPTS[1][0] <= recording_date <= RECORDING_ATTEMPTS[1][1]:
        colour = "b"
    elif RECORDING_ATTEMPTS[2][0] <= recording_date <= RECORDING_ATTEMPTS[2][1]:
        colour = "k"
    else:
        raise BaseException("Something is wrong.")
    colours[mea].append(colour)

    # compute mean firing rate
    if spikes.any():
        firing_rate = elephant.statistics.mean_firing_rate(spikes)
    else:
        firing_rate = 0
    fr_l[mea].append(firing_rate)

    # firing rate per channel
    if channels:
        for train in channels.values():
            fr_perchan = elephant.statistics.mean_firing_rate(train)
            age_perchan_l[mea].append(age)
            fr_perchan_l[mea].append(fr_perchan)
            colours_perchan[mea].append(colour)
    else:
        age_perchan_l[mea].append(age)
        fr_perchan_l[mea].append(0)
        fr_errors[mea][0].append(0)
        fr_errors[mea][1].append(0)
        colours_perchan[mea].append(colour)

    # number of active channels
    spike_trains = package.get_resource("spike-trains").read()
    active_channels_l[mea].append(len(spike_trains))

# plot data
figure, axes = plt.subplots(3, 1, sharex=True)
axes[0].scatter(age_l["2539"], fr_l["2539"], c=colours["2539"],
                marker="s", clip_on=False)
axes[0].scatter(age_l["2540"], fr_l["2540"], c=colours["2540"],
                marker="o", clip_on=False)
axes[0].set_xlabel("age / DIV")
axes[0].set_ylabel("population firing rate / $s^{-1}$")
handles = [Line2D([0], [0], marker="s", color="grey", lw=0, label="2539"),
           Line2D([0], [0], marker="o", color="grey", lw=0, label="2540"),
           Line2D([0], [0], color="r", lw=5, label="R1"),
           Line2D([0], [0], color="b", lw=5, label="R2"),
           Line2D([0], [0], color="k", lw=5, label="R3")]
axes[0].legend(handles=handles, loc="upper left", fontsize=6.0)

axes[1].scatter(age_perchan_l["2539"], fr_perchan_l["2539"],
                c=colours_perchan["2539"], marker="s",clip_on=False)
axes[1].scatter(age_perchan_l["2540"], fr_perchan_l["2540"],
                c=colours_perchan["2540"], marker="o",clip_on=False)
axes[1].set_xlabel("age / DIV")
axes[1].set_ylabel("channel firing rate / $s^{-1}$")

axes[2].scatter(age_l["2539"], active_channels_l["2539"], c=colours["2539"],
                marker="s", clip_on=False)
axes[2].scatter(age_l["2540"], active_channels_l["2540"], c=colours["2540"],
                marker="o", clip_on=False)
axes[2].set_xlabel("age / DIV")
axes[2].set_ylabel("active channels")

# add separation between x and y axes
for ax in axes:
    ax.spines["bottom"].set_position(["axes", -0.05])
    ax.set_ylim(bottom=0)

axes = axes.flatten()
h5fd.plot.label_panels(axes)
plt.savefig(FIGURE_FILE)
