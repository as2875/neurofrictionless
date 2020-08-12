# -*- coding: utf-8 -*-

import cycler
import datapackage
import h5fd.plot
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import quantities as qt
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import ListVector, FloatVector
import string
from tqdm import tqdm

# import meaRtools
meaRtools = importr("meaRtools")

def label_panel(ax, letter, *,
                offset_left=0.8, offset_up=0.2, prefix='', postfix='.', **font_kwds):
    kwds = dict(fontsize=12)
    kwds.update(font_kwds)
    # this mad looking bit of code says that we should put the code offset a certain distance in
    # inches (using the fig.dpi_scale_trans transformation) from the top left of the frame
    # (which is (0, 1) in ax.transAxes transformation space)
    fig = ax.figure
    trans = ax.transAxes + matplotlib.transforms.ScaledTranslation(-offset_left, offset_up, fig.dpi_scale_trans)
    ax.text(0, 1, prefix+letter+postfix, transform=trans, **kwds)

# plot parameters
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [6.69, 6.69]
matplotlib.rcParams["font.size"] = 6.0

# cycle through two colours only for bursts
burst_cycler = cycler.cycler(color=["r", "b"])
plt.rc("axes", prop_cycle=burst_cycler)

FIGURE_PATH = "../plots/burst_plots.pdf"
REPRESENTATIVE_PLOT_PATH = "../plots/supplementary_figures/raster_plots.pdf"

# location of data
DATA_DIR = "../data/2020-02-21_fd/"
data_files = sorted([os.path.join(DATA_DIR, file)
                     for file in os.listdir(DATA_DIR)])
REPRESENTATIVE_PLOTS = ["../data/2020-02-21_fd/170922_D15_2540.zip",
                        "../data/2020-02-21_fd/170927_D20_2540.zip",
                        "../data/2020-02-21_fd/171002_D25_2540.zip",
                        "../data/2020-02-21_fd/171013_D36_2540.zip"]

# parameters for burst detection
mi_par = ListVector({"beg_isi": 0.17,
                     "end_isi": 0.3,
                     "min_ibi": 0.2,
                     "min_durn": 0.05,
                     "min_spikes": 3})

# generate multipage PDF
count = 0
figure, axes = plt.subplots(2, 2, squeeze=False)
axes = axes.flatten()
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
        supp_figure, supp_axes = plt.subplots()
        y_offsets_map = h5fd.plot.rasterplot(channels, supp_axes, title, "s")
        if file in REPRESENTATIVE_PLOTS:
            h5fd.plot.rasterplot(channels, axes[count], "", "s", channel_labels=False)

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
                supp_axes.plot((spikes[start_b], spikes[end_b]),
                               (y_offsets_map[channel], y_offsets_map[channel]))

        pdf.savefig()
        if file in REPRESENTATIVE_PLOTS:
            count += 1
        plt.close()

for ax, letter in zip(axes, string.ascii_uppercase):
    label_panel(ax, letter)
figure.tight_layout()
figure.savefig(REPRESENTATIVE_PLOT_PATH)
