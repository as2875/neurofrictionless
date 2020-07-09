# -*- coding: utf-8 -*-

import datapackage
import os
import h5fd.plot
import quantities as qt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import ListVector, FloatVector

# import meaRtools
meaRtools = importr("meaRtools")

# plot parameters
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["font.size"] = 6.0
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
        _, channels, t_stop = h5fd.plot.extract_spike_trains(package,
                                                             qt.ms,
                                                             qt.s)

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

        pdf.savefig()
        plt.close()
