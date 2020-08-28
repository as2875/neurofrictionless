# -*- coding: utf-8 -*-

import datapackage
import elephant.statistics
import h5fd.plot
import itertools
import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy
import operator
import os
import pickle
import quantities as qt
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import ListVector, FloatVector
import random
import string
from tqdm import tqdm

# import meaRtools
meaRtools = importr("meaRtools")

# location of data
DATA_DIR = "../data/2020-02-21_fd/"
data_files = sorted([os.path.join(DATA_DIR, file)
                     for file in os.listdir(DATA_DIR)])

# plot parameters
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False

# location of combined figure
COMB_FIGURE_PATH = "../plots/supplementary_figures/isi_and_burst_example.pdf"

# ISI distribution
print("Analysing ISIs...")
FIGURE_PATH = "../plots/logisi_plots.pdf"
REPRESENTATIVE_BURSTD = "../data/2020-02-21_fd/180214_D35_2539.zip"

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
                                    squeeze=False,
                                    figsize=(6.69, 7.5))
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
        axes[count + 1].tick_params(axis="y", reset=True, right=False)
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
        bax.spines["top"].set_color("none")
        bax.spines["bottom"].set_color("none")
        bax.spines["left"].set_color("none")
        bax.spines["right"].set_color("none")
        bax.set_xticks([])
        bax.set_yticks([])
        bax.set_xticklabels([])
        bax.set_yticklabels([])
        bax.patch.set_alpha(0)
        bax.set_xlabel("interspike interval / s", labelpad=20)
        bax.set_ylabel("frequency", labelpad=25)
        figure.tight_layout()
        pdf.savefig()
        plt.close()

        if file == REPRESENTATIVE_BURSTD:
            # initialise figure 5
            comb_figure = plt.figure(figsize=(6.69, 7.5),
                                     constrained_layout=True)
            comb_spec = comb_figure.add_gridspec(
                                             nrows=x_dim*2,
                                             ncols=y_dim,
                                             figure=comb_figure
                                             )
            # axes for raster with bursts
            raster_axes = comb_figure.add_subplot(comb_spec[:x_dim, :y_dim])
            # dummy axes with axis labels
            comb_bax = comb_figure.add_subplot(comb_spec[x_dim:, :y_dim])

            # axes for histograms
            comb_axes = []
            for row in range(x_dim, 2*x_dim):
                for col in range(y_dim):
                    if len(comb_axes) > 0:
                        ax = comb_figure.add_subplot(comb_spec[row, col],
                                                     sharey=comb_axes[0],
                                                     sharex=comb_axes[0])
                    else:
                        ax = comb_figure.add_subplot(comb_spec[row, col])
                    if row != 2*x_dim - 1:
                       ax.tick_params(labelbottom=False)
                    if col != 0:
                        ax.tick_params(labelleft=False)
                    comb_axes.append(ax)

            count = len(comb_axes) - 1
            for channel, spikes in sorted(channels.items()):
                isi = elephant.statistics.isi(spikes)
                isi = [math.log10(float(interval)) for interval in isi]
                comb_axes[count].hist(isi, bins="auto", color="g")
                comb_axes[count].text(0.75, 0.9,
                                      "ch. " + channel,
                                      fontsize=8.0,
                                      transform=comb_axes[count].transAxes)
                lim = [round(l) for l in comb_axes[count].get_xlim()]
                comb_axes[count].set_xlim(lim)
                count -= 1
            comb_axes[count + 1].tick_params(labelleft=True)
            comb_figure.canvas.draw()

            # replace log labels with linear labels
            for ax in comb_axes:
                xlabels = [t.get_text().replace("−", "-") for t in ax.get_xticklabels()]
                xlabels = [x for x in xlabels if x]
                if not xlabels:
                    continue
                xlabels = [10**float(x) for x in xlabels]
                xlabels_rounded = []
                for x in xlabels:
                    if operator.mod(x, 1) == 0:
                        xlabels_rounded.append(int(x))
                    else:
                        xlabels_rounded.append(x)
                ax.set_xticklabels(xlabels_rounded)

            while count >= 0:
                comb_axes[count].set_axis_off()
                count -= 1
            # overall axis titles
            comb_bax.spines["top"].set_color("none")
            comb_bax.spines["bottom"].set_color("none")
            comb_bax.spines["left"].set_color("none")
            comb_bax.spines["right"].set_color("none")
            comb_bax.set_xticks([])
            comb_bax.set_yticks([])
            comb_bax.set_xticklabels([])
            comb_bax.set_yticklabels([])
            comb_bax.patch.set_alpha(0)
            comb_bax.set_xlabel("interspike interval / s", labelpad=20)
            comb_bax.set_ylabel("frequency", labelpad=25)

# burst detection
print("Detecting bursts...")
FIGURE_PATH = "../plots/burst_plots.pdf"
REPRESENTATIVE_PLOT_PATH = "../plots/supplementary_figures/raster_plots.pdf"
REPRESENTATIVE_PLOTS = ["../data/2020-02-21_fd/170922_D15_2540.zip",
                        "../data/2020-02-21_fd/170927_D20_2540.zip",
                        "../data/2020-02-21_fd/171002_D25_2540.zip",
                        "../data/2020-02-21_fd/171013_D36_2540.zip"]

# parameters for burst detection
mi_par = ListVector({"beg_isi": 0.17,
                     "end_isi": 0.3,
                     "min_ibi": 0.2,
                     "min_durn": 0.01,
                     "min_spikes": 3})

# generate multipage PDF
count = 0
figure, axes = plt.subplots(2, 2,
                            sharex=True,
                            figsize=(6.69, 6.69))
axes = axes.flatten()
age_labels = []
with PdfPages(FIGURE_PATH) as pdf:
    for file in tqdm(data_files):
        package = datapackage.Package(file)
        _, channels, t_stop = h5fd.plot.extract_spike_trains(package,
                                                             qt.ms,
                                                             qt.s)
        date = package.descriptor["meta"]["date"]
        age = str(package.descriptor["meta"]["age"])
        mea = package.descriptor["meta"]["MEA"]
        title = date + " " + "D" + age + " " + "R" + mea

        # raster plot
        supp_figure, supp_axes = plt.subplots(constrained_layout=True)
        y_offsets_map = h5fd.plot.rasterplot(channels, supp_axes, title, "s")
        if file in REPRESENTATIVE_PLOTS:
            h5fd.plot.rasterplot(channels, axes[count], "", "s", channel_labels=False)
            age_labels.append("DPI " + str(age))
            if count == 0:
                axes[count].plot((0, 20), (-1, -1), "k")
                axes[count].text(25, -1, "20 s", va="center")
        if file == REPRESENTATIVE_BURSTD:
            h5fd.plot.rasterplot(channels, raster_axes, "", "s", spike_count=False)
            raster_axes.spines["bottom"].set_color("none")
            raster_axes.spines["left"].set_color("none")
            raster_axes.tick_params(left=False)
            raster_axes.set_xticks([])
            raster_axes.set_xticklabels([])
            raster_axes.set_xlabel("")
            raster_axes.set_xlim(left=-0.1)
            raster_axes.plot((0, 20), (-1, -1), "k")
            raster_axes.text(25, -1, "20 s", va="center")

        if y_offsets_map is None:
            pdf.savefig()
            plt.close()
            continue

        for channel, spikes in channels.items():
            # buRst detection
            spikes_vec = FloatVector(spikes)
            allb = meaRtools.mi_find_bursts(spikes_vec, mi_par)
            for i, off in zip(range(1, allb.nrow + 1), itertools.cycle([-0.1, 0.1])):
                burst = allb.rx(i, True)  # extract ith row
                start_b = int(burst[0]) - 1
                end_b = int(burst[1]) - 1
                supp_axes.plot((spikes[start_b], spikes[end_b]),
                               (y_offsets_map[channel] + off, y_offsets_map[channel] + off),
                               color="g")
                if file == REPRESENTATIVE_BURSTD:
                    raster_axes.plot((spikes[start_b], spikes[end_b]),
                                     (y_offsets_map[channel], y_offsets_map[channel]),
                                     color="g", lw=4)

        if file in REPRESENTATIVE_PLOTS:
            count += 1

        pdf.savefig()
        plt.close()

h5fd.plot.label_panels(axes, labels=age_labels)
figure.tight_layout()
figure.savefig(REPRESENTATIVE_PLOT_PATH)

h5fd.plot.label_panels([raster_axes, comb_bax])
comb_figure.savefig(COMB_FIGURE_PATH)
