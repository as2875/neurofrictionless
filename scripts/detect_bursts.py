# -*- coding: utf-8 -*-

import datapackage
import os
import h5fd.plot
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import ListVector, FloatVector

# import meaRtools
meaRtools = importr("meaRtools")

# plot parameters
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["font.size"] = 8.0
FIGURE_PATH = "../plots/burst_plots.pdf"

# location of data
DATA_DIR = "../data/2020-02-21_fd/"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

# parameters for burst detection
mi_par = ListVector({"beg_isi": 0.17,
                     "end_isi": 0.3,
                     "min_ibi": 0.2,
                     "min_durn": 0.05,
                     "min_spikes": 3})

with PdfPages(FIGURE_PATH) as pdf:
    for file in data_files:
        package = datapackage.Package(file)
        channels, t_stop = {}, 0
        for row in package.get_resource("spikes").read(keyed=True, relations=True):
            spike_time = float(row["time"]) / 1000
            index = row["spike-train-index"]["epos-x"] + \
                row["spike-train-index"]["epos-y"]
            if index not in channels.keys():
                channels[index] = []
            channels[index].append(spike_time)
            if spike_time > t_stop:
                t_stop = spike_time

        # raster plot
        figure, axes = plt.subplots()
        y_offsets_map = h5fd.plot.rasterplot(channels, axes, file, "s")

        if y_offsets_map is None:
            pdf.savefig()
            plt.close()
            continue

        for channel, spikes in channels.items():
            # buRst deteRction
            spikes_vec = FloatVector(spikes)
            allb = meaRtools.mi_find_bursts(spikes_vec, mi_par)
            for i in range(1, allb.nrow + 1):
                burst = allb.rx(i, True)  # extract ith row
                start_b = int(burst[0]) - 1
                end_b = int(burst[1]) - 1
                axes.plot((spikes[start_b], spikes[end_b]),
                          (y_offsets_map[channel], y_offsets_map[channel]))
        figure.tight_layout()
        pdf.savefig()
        plt.close()
