# -*- coding: utf-8 -*-

import elephant
import neo
import os
import quantities as qt
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

matplotlib.rcParams["figure.dpi"] = 300
DATA_DIR = "../data/2020-02-21/"
PLOTS_FILE = "../data/plots.pdf"
data_files = [ os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR) if file.endswith(".txt") ]

with PdfPages(PLOTS_FILE) as pdf:
    for file in data_files:
        # setup
        index_pattern = re.compile(r"(?<=Spikes \d )\d\d")
        whitespace_pattern = re.compile(r"\s+")

        # read file
        with open(file) as f:
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

        if not spikes:
            continue

        # convert to neo SpikeTrain, makes for easier processing later on
        for index in spikes.keys():
            spikes[index] = neo.SpikeTrain(times=spikes[index]*qt.ms,
                                           t_stop=t_stop)

        # plot data
        # event plot
        plt.figure()
        labels = list(spikes.keys())
        events = [spikes[label] for label in labels]
        plt.eventplot(events, linelengths=0.75, color="black", lw=0.2)
        plt.yticks(list(range(len(labels))), labels=labels)
        plt.xlabel("time / ms")
        plt.ylabel("channel")
        plt.title(file)
        pdf.savefig()
        plt.close()

        # plate summary
        plt.figure()
        # generate coordinates
        x, y = zip(*[(int(index[0]), int(index[1])) for index in spikes.keys()])
        plt.xlim([0, 9])
        plt.ylim([0, 9])
        plt.plot(x, y, "kx")
        for index in spikes.keys():  # add annotations
            plt.annotate("ch" + index,
                         xy=(int(index[0]), int(index[1])))
        plt.title(file)
        pdf.savefig()
        plt.close()

        # firing rate
        hist = elephant.statistics.time_histogram(spikes.values(),
                                                  500*qt.ms,
                                                  output="rate")
        plt.figure()
        plt.bar(hist.times, hist.T[0], width=500, color="black")
        plt.xlabel("time / $ms$")
        plt.ylabel("rate / $ms^{-1}$")
        plt.title(file)
        plt.tight_layout()
        pdf.savefig()
        plt.close()
