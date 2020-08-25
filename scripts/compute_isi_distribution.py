# -*- coding: utf-8 -*-

import datapackage
import elephant.statistics
import h5fd.plot
import itertools
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy
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
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/logisi_plots.pdf"
REPRESENTATIVE_PLOT_PATH = "../plots/supplementary_figures/logisi_plot_example.pdf"
REPRESENTATIVE_PLOTS = ["../data/2020-02-21_fd/180214_D35_2539.zip"]
# data_files = sorted([os.path.join(DATA_DIR, file)
#                      for file in os.listdir(DATA_DIR)])
data_files = REPRESENTATIVE_PLOTS

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

        count = len(axes) - 1
        for channel, spikes in sorted(channels.items()):
            isi = elephant.statistics.isi(spikes)
            isi = [math.log10(float(interval)) for interval in isi]
            axes[count].hist(isi, bins="auto", color="g")
            axes[count].text(0.75, 0.9,
                             "ch. " + channel,
                             transform=axes[count].transAxes)
            lim = [round(l) for l in axes[count].get_xlim()]
            axes[count].set_xlim(lim)
            count -= 1
        figure.canvas.draw()
        # replace log labels with linear labels
        for ax in axes:
            xlabels = [t.get_text().replace("−", "-") for t in ax.get_xticklabels()]
            xlabels = [10**float(x) for x in xlabels]
            xlabels = [round(x) for x in xlabels]
            ax.set_xticklabels(xlabels)
        while count >= 0:
            axes[count].set_axis_off()
            count -= 1

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
        bax.set_xlabel("ISI / s", labelpad=20)
        bax.set_ylabel("frequency density", labelpad=25)
        figure.tight_layout()

        if file in REPRESENTATIVE_PLOTS:
            figure.suptitle("")
            rpdf.savefig()
        pdf.savefig()
        plt.close()
