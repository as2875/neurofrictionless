# -*- coding: utf-8 -*-

import datapackage
import neo
import os
import elephant.statistics
import matplotlib
import matplotlib.pyplot as plt
import quantities as qt

# adjust matplotlib parameters
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["font.size"] = 8.0

DATA_DIR = "../data/2020-02-21_fd/"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

age_l, fr_l, N_l, active_channels_l, ts_l = [], [], [], [], []
for file in data_files:
    # load package
    package = datapackage.Package(file)

    # spike times
    spikes, t_stop = [], 0
    for row in package.get_resource("spikes").read(keyed=True):
        spike_time = float(row["time"])
        spikes.append(spike_time)
        if spike_time > t_stop:
            t_stop = spike_time

    # convert to neo SpikeTrain
    spikes = neo.SpikeTrain(spikes * qt.ms, t_stop)

    age = package.descriptor["meta"]["age"]
    age_l.append(age)

    # compute mean firing rate
    if spikes.any():
        firing_rate = elephant.statistics.mean_firing_rate(spikes)
    else:
        firing_rate = None
    fr_l.append(firing_rate*1000)

    # number of spikes
    N_l.append(len(spikes))

    # number of active channels
    spike_trains = package.get_resource("spike-trains").read()
    active_channels_l.append(len(spike_trains))

    # computed recording time
    ts_l.append(t_stop/1000)

# plot data
figure, axes = plt.subplots(2, 2)
# top left
axes[0, 0].plot(age_l, fr_l, "k.")
axes[0, 0].set_xlabel("age / DIV")
axes[0, 0].set_ylabel("firing rate / $s^{-1}$")
# top right
axes[0, 1].plot(age_l, N_l, "k.")
axes[0, 1].set_xlabel("age / DIV")
axes[0, 1].set_ylabel("number of spikes")
# bottom left
axes[1, 0].plot(age_l, active_channels_l, "k.")
axes[1, 0].set_xlabel("age / DIV")
axes[1, 0].set_ylabel("active channels")
# bottom right
axes[1, 1].plot(age_l, ts_l, "k.")
axes[1, 1].set_xlabel("age / DIV")
axes[1, 1].set_ylabel("recording time / $s$")
figure.tight_layout()
