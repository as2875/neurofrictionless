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
matplotlib.rcParams["figure.figsize"] = [6.69, 7.5]
matplotlib.rcParams["font.size"] = 8.0
matplotlib.rcParams["figure.constrained_layout.use"] = True

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/logisi_plots.pdf"
REPRESENTATIVE_PLOT_PATH = "../plots/supplementary_figures/logisi_plot_example.pdf"
REPRESENTATIVE_PLOTS = ["../data/2020-02-21_fd/171002_D25_2540.zip",
                        "../data/2020-02-21_fd/171013_D36_2540.zip"]
data_files = sorted([os.path.join(DATA_DIR, file)
                     for file in os.listdir(DATA_DIR)])

with PdfPages(FIGURE_PATH) as pdf, \
     PdfPages(REPRESENTATIVE_PLOT_PATH) as rpdf:
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

        x_dim = math.ceil(math.sqrt(len(channels)))
        if x_dim == 0:
            figure, axes = plt.subplots()
            figure.suptitle(title)
            axes.set_axis_off()
            pdf.savefig()
            continue
        y_dim = math.ceil(len(channels) / x_dim)

        figure, axes = plt.subplots(nrows=x_dim, ncols=y_dim,
                                    sharex=True, sharey=True,
                                    constrained_layout=False,
                                    squeeze=False)
        axes = axes.flatten()
        bax = figure.add_subplot(111)

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
        bax.spines['top'].set_color('none')
        bax.spines['bottom'].set_color('none')
        bax.spines['left'].set_color('none')
        bax.spines['right'].set_color('none')
        bax.set_xticks([])
        bax.set_yticks([])
        bax.set_xticklabels([])
        bax.set_yticklabels([])
        bax.patch.set_alpha(0)
        bax.set_xlabel("$\log$ ISI", labelpad=20)
        bax.set_ylabel("frequency density", labelpad=25)
        figure.tight_layout()

        if file in REPRESENTATIVE_PLOTS:
            figure.suptitle("")
            rpdf.savefig()
        pdf.savefig()
        plt.close()
