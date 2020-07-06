# -*- coding: utf-8 -*-

import datapackage
import neo
import os
import statistics
import elephant.statistics
import matplotlib
import matplotlib.pyplot as plt
import quantities as qt

# adjust matplotlib parameters
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [10, 5]
matplotlib.rcParams["font.size"] = 8.0

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_FILE = "../plots/development_plots.pdf"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

age_l, fr_l, N_l, active_channels_l, ts_l, fr_perchan_l = \
    [], [], [], [], [], []
fr_errors = [[],[]]
for file in data_files:
    # load package
    package = datapackage.Package(file)

    # spike times
    spikes, channels, t_stop = [], {}, 0
    for row in package.get_resource("spikes").read(keyed=True):
        spike_time = float(row["time"])
        spikes.append(spike_time)
        index = row["spike-train-index"]
        if index not in channels.keys():
            channels[index] = []
        channels[index].append(spike_time)
        if spike_time > t_stop:
            t_stop = spike_time

    # convert to neo SpikeTrain
    spikes = neo.SpikeTrain(spikes * qt.ms, t_stop)
    for k in channels.keys():
        channels[k] = neo.SpikeTrain(channels[k] * qt.ms, t_stop)

    age = package.descriptor["meta"]["age"]
    age_l.append(age)

    # compute mean firing rate
    if spikes.any():
        firing_rate = elephant.statistics.mean_firing_rate(spikes)
        firing_rate.rescale(1/qt.s)
    else:
        firing_rate = None
    fr_l.append(firing_rate)

    # firing rate per channel
    if channels:
        channel_fr = [float(
            elephant.statistics.mean_firing_rate(train).rescale(1/qt.s))
                      for train in channels.values()]
        mean_fr = statistics.mean(channel_fr)
        fr_perchan_l.append(mean_fr)
        # upper errors
        fr_errors[1].append(
            max(channel_fr) - mean_fr
            )
        # lower errors
        fr_errors[0].append(
            mean_fr - min(channel_fr)
            )
    else:
        fr_perchan_l.append(0)
        fr_errors[0].append(0)
        fr_errors[1].append(0)

    # number of spikes
    N_l.append(len(spikes))

    # number of active channels
    spike_trains = package.get_resource("spike-trains").read()
    active_channels_l.append(len(spike_trains))

    # computed recording time
    ts_l.append(t_stop/1000)

# plot data
figure, axes = plt.subplots(2, 3)

axes[0, 0].plot(age_l, fr_l, "k.")
axes[0, 0].set_xlabel("age / DIV")
axes[0, 0].set_ylabel("firing rate / $s^{-1}$")

axes[0, 1].plot(age_l, N_l, "k.")
axes[0, 1].set_xlabel("age / DIV")
axes[0, 1].set_ylabel("number of spikes")

axes[0, 2].plot(age_l, active_channels_l, "k.")
axes[0, 2].set_xlabel("age / DIV")
axes[0, 2].set_ylabel("active channels")

axes[1, 0].plot(age_l, ts_l, "k.")
axes[1, 0].set_xlabel("age / DIV")
axes[1, 0].set_ylabel("recording time / $s$")

axes[1, 1].errorbar(age_l, fr_perchan_l, fmt="k.", yerr=fr_errors)
axes[1, 1].set_xlabel("age / DIV")
axes[1, 1].set_ylabel("firing rate\nper channel / $s^{-1}$")

axes[1, 2].set_axis_off()

# save figure
figure.tight_layout()
figure.savefig(FIGURE_FILE)
