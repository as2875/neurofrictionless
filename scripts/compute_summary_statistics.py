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

# adjust matplotlib parameters
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [5, 5]
matplotlib.rcParams["figure.constrained_layout.use"] = True
matplotlib.rcParams["font.size"] = 12.0

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_FILE = "../plots/development_plots_"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

age_l, fr_l, N_l, active_channels_l, ts_l, fr_perchan_l, colours =\
    ({"2539": [], "2540": []} for i in range(7))
fr_errors = {"2539": [[], []], "2540": [[], []]}
for file in data_files:
    # load package
    package = datapackage.Package(file)
    mea = package.descriptor["meta"]["MEA"]

    # spike times
    spikes, channels, t_stop = h5fd.plot.extract_spike_trains(package,
                                                              qt.ms,
                                                              qt.s)

    age = package.descriptor["meta"]["age"]
    age_l[mea].append(age)

    # compute mean firing rate
    if spikes.any():
        firing_rate = elephant.statistics.mean_firing_rate(spikes)
    else:
        firing_rate = 0
    fr_l[mea].append(firing_rate)

    # firing rate per channel
    if channels:
        channel_fr = [float(
            elephant.statistics.mean_firing_rate(train))
                      for train in channels.values()]
        mean_fr = statistics.mean(channel_fr)
        fr_perchan_l[mea].append(mean_fr)
        # upper errors
        fr_errors[mea][1].append(
            max(channel_fr) - mean_fr
            )
        # lower errors
        fr_errors[mea][0].append(
            mean_fr - min(channel_fr)
            )
    else:
        fr_perchan_l[mea].append(0)
        fr_errors[mea][0].append(0)
        fr_errors[mea][1].append(0)

    # number of spikes
    N_l[mea].append(len(spikes))

    # number of active channels
    spike_trains = package.get_resource("spike-trains").read()
    active_channels_l[mea].append(len(spike_trains))

    # computed recording time
    ts_l[mea].append(t_stop)

    datestamp = package.descriptor["meta"]["date"]
    recording_date = datetime.date(int("20" + datestamp[:2]),
                                   int(datestamp[2:4]),
                                   int(datestamp[4:]))
    if RECORDING_ATTEMPTS[0][0] <= recording_date <= RECORDING_ATTEMPTS[0][1]:
        colours[mea].append("r")
    elif RECORDING_ATTEMPTS[1][0] <= recording_date <= RECORDING_ATTEMPTS[1][1]:
        colours[mea].append("b")
    elif RECORDING_ATTEMPTS[2][0] <= recording_date <= RECORDING_ATTEMPTS[2][1]:
        colours[mea].append("k")
    else:
        raise BaseException("Something is wrong.")

# plot data
figure, axes = plt.subplots()
axes.scatter(age_l["2539"], fr_l["2539"], c=colours["2539"], marker="s")
axes.scatter(age_l["2540"], fr_l["2540"], c=colours["2540"], marker="o")
axes.set_xlabel("age / DIV")
axes.set_ylabel("firing rate / $s^{-1}$")
handles = [Line2D([0], [0], marker="s", color="grey", lw=0, label="2539"),
           Line2D([0], [0], marker="o", color="grey", lw=0, label="2540"),
           Line2D([0], [0], color="r", lw=5, label="R1"),
           Line2D([0], [0], color="b", lw=5, label="R2"),
           Line2D([0], [0], color="k", lw=5, label="R3")]
axes.legend(handles=handles)
plt.savefig(FIGURE_FILE + "fr.png")
plt.close()

figure, axes = plt.subplots()
axes.scatter(age_l["2539"], N_l["2539"], c=colours["2539"], marker="s")
axes.scatter(age_l["2540"], N_l["2540"], c=colours["2540"], marker="o")
axes.set_xlabel("age / DIV")
axes.set_ylabel("number of spikes")
plt.savefig(FIGURE_FILE + "n.png")
plt.close()

figure, axes = plt.subplots()
axes.scatter(age_l["2539"], active_channels_l["2539"], c=colours["2539"],
             marker="s")
axes.scatter(age_l["2540"], active_channels_l["2540"], c=colours["2540"],
             marker="o")
axes.set_xlabel("age / DIV")
axes.set_ylabel("active channels")
plt.savefig(FIGURE_FILE + "channels.png")
plt.close()

figure, axes = plt.subplots()
axes.scatter(age_l["2539"], ts_l["2539"], c=colours["2539"], marker="s")
axes.scatter(age_l["2540"], ts_l["2540"], c=colours["2540"], marker="o")
axes.set_xlabel("age / DIV")
axes.set_ylabel("recording time / $s$")
plt.savefig(FIGURE_FILE + "recording_time.png")
plt.close()

figure, axes = plt.subplots()
axes.scatter(age_l["2539"], fr_perchan_l["2539"], c=colours["2539"],
             marker="s")
axes.scatter(age_l["2540"], fr_perchan_l["2540"], c=colours["2540"],
             marker="o")
axes.errorbar(age_l["2539"], fr_perchan_l["2539"], fmt="none",
              yerr=fr_errors["2539"], ecolor="k")
axes.errorbar(age_l["2540"], fr_perchan_l["2540"], fmt="none",
              yerr=fr_errors["2540"], ecolor="k")
axes.set_xlabel("age / DIV")
axes.set_ylabel("firing rate\nper channel / $s^{-1}$")
plt.savefig(FIGURE_FILE + "fr_perchan.png")
plt.close()
