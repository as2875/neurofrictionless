# -*- coding: utf-8 -*-

import datapackage
import elephant.statistics
import h5fd.plot
import itertools
import math
import matplotlib
import matplotlib.pyplot as plt
import os
import quantities as qt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

# plotting parameters
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [10, 10]
matplotlib.rcParams["font.size"] = 8.0
matplotlib.rcParams["figure.constrained_layout.use"] = True

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/logisi_plots.pdf"
REPRESENTATIVE_PLOT_PATH = "../plots/supplementary_figures/logisi_plot_example.png"
REPRESENTATIVE_PLOT = "../data/2020-02-21_fd/171013_D36_2540.zip"
data_files = sorted([os.path.join(DATA_DIR, file)
                     for file in os.listdir(DATA_DIR)])

with PdfPages(FIGURE_PATH) as pdf:
    for file in tqdm(data_files):
        # load package
        package = datapackage.Package(file)
        _, channels, t_stop = h5fd.plot.extract_spike_trains(package,
                                                             qt.ms,
                                                             qt.s)
        date = package.descriptor["meta"]["date"]
        age = str(package.descriptor["meta"]["age"])
        mea = package.descriptor["meta"]["MEA"]
        title = date + " " + "D" + age + " " + "R" + mea

        dim = math.ceil(math.sqrt(len(channels)))
        if dim == 0:
            figure, axes = plt.subplots()
            figure.suptitle(title)
            axes.set_axis_off()
            pdf.savefig()
            continue

        figure, axes = plt.subplots(dim, dim, squeeze=False)
        axes = list(itertools.chain(*axes))

        count = 0
        for channel, spikes in sorted(channels.items()):
            isi = elephant.statistics.isi(spikes)
            isi = [math.log10(float(interval)) for interval in isi]
            axes[count].hist(isi,
                             bins="auto")
            axes[count].set_title(channel)
            count += 1
        for i in range(count, len(axes)):
            axes[i].set_axis_off()
        figure.suptitle(title)
        if file == REPRESENTATIVE_PLOT:
            figure.savefig(REPRESENTATIVE_PLOT_PATH)
        pdf.savefig()
        plt.close()
