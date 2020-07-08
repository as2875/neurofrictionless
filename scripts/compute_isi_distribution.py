# -*- coding: utf-8 -*-

import datapackage
import elephant.statistics
import h5fd.plot
import math
import matplotlib
import matplotlib.pyplot as plt
import os
import quantities as qt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

# plotting parameters
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [20, 20]
matplotlib.rcParams["font.size"] = 8.0
matplotlib.rcParams["figure.constrained_layout.use"] = True

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/logisi_plots.pdf"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

with PdfPages(FIGURE_PATH) as pdf:
    for file in tqdm(data_files):
        # load package
        package = datapackage.Package(file)
        _, channels, t_stop = h5fd.plot.extract_spike_trains(package, qt.ms)

        figure, axes = plt.subplots(8, 8)
        for i in range(len(axes)):
            for j in range(len(axes[i])):
                label = str(i + 1) + str(j + 1)
                if label in channels.keys():
                    spikes = channels[label]
                    isi = elephant.statistics.isi(spikes)
                    isi = isi.rescale(qt.s)
                    isi = [math.log(float(interval)) for interval in isi]
                    axes[i, j].hist(isi,
                                    bins="auto")
                    axes[i, j].set_title(label)
                else:
                    axes[i, j].set_axis_off()
        figure.suptitle(file)
        pdf.savefig()
        plt.close()
