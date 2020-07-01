# -*- coding: utf-8 -*-

import elephant
import neo
import os
import quantities as qt
import re
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams["figure.dpi"] = 300

# setup
SOURCE_FILENAME = "../data/170927_D20_2540.txt"
basename = os.path.splitext(SOURCE_FILENAME)[0]
index_pattern = re.compile(r"(?<=Spikes \d )\d\d")
whitespace_pattern = re.compile(r"\s+")

# read file
with open(SOURCE_FILENAME) as f:
    data = f.read()

# extract spike times from file
channels = data.split("\n\n\n")
channels = channels[1:]  # remove heading

spikes = dict()
t_stop = 0
for channel in channels:
    waveforms = [spike.strip().split("\n")
                 for spike in channel.strip().split("\n\n")]
    # exclude empty channels
    if len(waveforms) <= 2:
        continue

    index = re.search(index_pattern, channel)
    index = index.group(0)
    spikes[index] = list()

    for wave in waveforms:
        spike_time = float(re.split(whitespace_pattern, wave[25])[0])
        if spike_time > t_stop:
            t_stop = spike_time
        spikes[index].append(spike_time)

# convert to neo SpikeTrain, makes for easier processing later on
for index in spikes.keys():
    spikes[index] = neo.SpikeTrain(times=spikes[index]*qt.ms,
                                   t_stop=t_stop)

# plot data
# event plot
figure_1, axes_1 = plt.subplots()
labels = list(spikes.keys())
events = [spikes[label] for label in labels]
axes_1.eventplot(events, linelengths=0.75, color="black", lw=0.2)
plt.yticks(list(range(len(labels))), labels=labels)
plt.xlabel("time / ms")
plt.ylabel("channel")
plt.title(SOURCE_FILENAME)

# plate summary
figure_2, axes_2 = plt.subplots()
# generate coordinates
x, y = zip(*[(int(index[0]), int(index[1])) for index in spikes.keys()])
axes_2.set_xlim([0, 9])
axes_2.set_ylim([0, 9])
axes_2.plot(x, y, "kx")
for index in spikes.keys():  # add annotations
    axes_2.annotate("ch" + index,
                    xy=(int(index[0]), int(index[1])))
plt.title(SOURCE_FILENAME)

# firing rate
hist = elephant.statistics.time_histogram(spikes.values(),
                                          500*qt.ms,
                                          output="rate")
figure_3, axes_3 = plt.subplots()
axes_3.bar(hist.times, hist.T[0], width=500, color="black")
plt.xlabel("time / $ms$")
plt.ylabel("rate / $ms^{-1}$")
plt.title(SOURCE_FILENAME)
