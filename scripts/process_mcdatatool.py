# -*- coding: utf-8 -*-

import neo
import os
import re
import matplotlib
import matplotlib.pyplot as plt
import quantities as pq

matplotlib.rcParams["figure.dpi"] = 300

# Setup
SOURCE_FILENAME = "../data/170927_D20_2540.txt"
basename = os.path.splitext(SOURCE_FILENAME)[0]
index_pattern = re.compile(r"(?<=Spikes \d )\d\d")
whitespace_pattern = re.compile(r"\s+")

# Read file
with open(SOURCE_FILENAME) as f:
    data = f.read()

# Extract spike times from file
channels = data.split("\n\n\n")
channels = channels[1:]  # remove heading

spikes = dict()
for channel in channels:
    waveforms = [spike.strip().split("\n")
                 for spike in channel.strip().split("\n\n")]
    # exclude empty channels
    if len(waveforms) <= 2:
        continue

    index = re.search(index_pattern, channel)
    index = int(index.group(0))
    spikes[index] = list()

    for wave in waveforms:
        spike_time = float(re.split(whitespace_pattern, wave[25])[0])
        spikes[index].append(spike_time)

    spikes[index] = neo.SpikeTrain(spikes[index]*pq.ms, spikes[index][-1])

# Plot data
figure, axes = plt.subplots(len(spikes), 1)
figure.tight_layout()
title_font = {"fontsize": 5}
for axis, channel in zip(axes, spikes.keys()):
    axis.set_axis_off()
    axis.set_title("Channel " + str(channel),
                   fontdict=title_font)
    axis.eventplot(spikes[channel],
                   linewidths=0.1,
                   colors="k")
