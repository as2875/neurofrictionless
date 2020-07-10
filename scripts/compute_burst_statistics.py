# -*- coding: utf-8 -*-

import datapackage
import datetime
import h5fd.plot
from h5fd.plot import RECORDING_ATTEMPTS
import os
import quantities as qt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import ListVector, FloatVector

# import meaRtools
meaRtools = importr("meaRtools")

# adjust matplotlib parameters
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [10, 10]
matplotlib.rcParams["font.size"] = 5.0

# get filenames
DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/burst_boxplots.pdf"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

# parameters for burst detection
mi_par = ListVector({"beg_isi": 0.17,
                     "end_isi": 0.3,
                     "min_ibi": 0.2,
                     "min_durn": 0.05,
                     "min_spikes": 3})

# displacement of plots
age_l = []

# bfq: freqency of bursts
# bdn: duration of bursts
# bfr: firing rate in burst
# bpc: percentage of spikes in burst
bfq_l, bdn_l, bfr_l, bpc_l = [], [], [], []

# location in each of the lists
count = 0

# colour of boxes
colours = {"by-replicate": [], "by-recording": []}

for file in data_files:
    # extract data
    package = datapackage.Package(file)
    _, channels, t_stop = h5fd.plot.extract_spike_trains(package,
                                                         qt.ms,
                                                         output_unit=qt.s,
                                                         threshold=10*(1/qt.min))

    # add the age
    age_l.append(int(package.descriptor["meta"]["age"]))

    # make an empty vector in each list
    bfq_l.append([])
    bdn_l.append([])
    bfr_l.append([])
    bpc_l.append([])

    for spikes in channels.values():
        spikes_vec = FloatVector(spikes)
        allb = meaRtools.mi_find_bursts(spikes_vec, mi_par)

        # calculate summary statistics
        # frequency of bursts
        bfq = allb.nrow / t_stop
        bfq_l[count].append(bfq)

        # running total of number of spikes in bursts
        tbn = 0
        for i in range(1, allb.nrow + 1):
            burst = allb.rx(i, True)  # extract ith row

            # duration of bursts
            start_b = int(burst[0]) - 1
            end_b = int(burst[1]) - 1
            bdn = spikes[end_b] - spikes[start_b]
            bdn_l[count].append(bdn)

            # firing rate in burst
            bn = burst[1] - burst[0] + 1  # number of spikes in burst
            bfr = bn/bdn
            bfr_l[count].append(bfr)

            # add number of spikes to running total
            tbn += bn

        # percentage of spikes in bursts
        bpc = (tbn / len(spikes)) * 100
        bpc_l[count].append(bpc)
    if package.descriptor["meta"]["MEA"] == "2539":
        colours["by-replicate"].append("r")
    else:
        colours["by-replicate"].append("b")

    datestamp = package.descriptor["meta"]["date"]
    recording_date = datetime.date(int("20" + datestamp[:2]),
                                   int(datestamp[2:4]),
                                   int(datestamp[4:]))
    if RECORDING_ATTEMPTS[0][0] <= recording_date <= RECORDING_ATTEMPTS[0][1]:
        colours["by-recording"].append("r")
    elif RECORDING_ATTEMPTS[1][0] <= recording_date <= RECORDING_ATTEMPTS[1][1]:
        colours["by-recording"].append("b")
    else:
        colours["by-recording"].append("k")

    count += 1

with PdfPages(FIGURE_PATH) as pdf:
    # box plots
    # colour code by replicate
    figure, axes = plt.subplots(2, 2)

    # frequency of bursts
    bplot_bfq = axes[0, 0].boxplot(bfq_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[0, 0].set_xlabel("age / DIV")
    axes[0, 0].set_ylabel("bursts per second / $s^{-1}$")

    # duration of bursts
    bplot_bdn = axes[0, 1].boxplot(bdn_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[0, 1].set_xlabel("age / DIV")
    axes[0, 1].set_ylabel("burst duration / s")

    # firing rate in burst
    bplot_bfr = axes[1, 0].boxplot(bfr_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[1, 0].set_xlabel("age / DIV")
    axes[1, 0].set_ylabel("firing rate in burst / $s^{-1}$")

    # percentage of spikes in bursts
    bplot_bpc = axes[1, 1].boxplot(bpc_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[1, 1].set_xlabel("age / DIV")
    axes[1, 1].set_ylabel("% spikes in bursts")

    for bplot in (bplot_bfq, bplot_bdn, bplot_bfr, bplot_bpc):
        for patch, colour in zip(bplot['boxes'], colours["by-replicate"]):
            patch.set_facecolor(colour)
    figure.suptitle("Plots by replicate")
    pdf.savefig(figure)

    # colour code by recording date
    figure, axes = plt.subplots(2, 2)

    # frequency of bursts
    bplot_bfq = axes[0, 0].boxplot(bfq_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[0, 0].set_xlabel("age / DIV")
    axes[0, 0].set_ylabel("bursts per second / $s^{-1}$")

    # duration of bursts
    bplot_bdn = axes[0, 1].boxplot(bdn_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[0, 1].set_xlabel("age / DIV")
    axes[0, 1].set_ylabel("burst duration / s")

    # firing rate in burst
    bplot_bfr = axes[1, 0].boxplot(bfr_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[1, 0].set_xlabel("age / DIV")
    axes[1, 0].set_ylabel("firing rate in burst / $s^{-1}$")

    # percentage of spikes in bursts
    bplot_bpc = axes[1, 1].boxplot(bpc_l,
                                   positions=age_l,
                                   sym="",
                                   patch_artist=True)
    axes[1, 1].set_xlabel("age / DIV")
    axes[1, 1].set_ylabel("% spikes in bursts")

    for bplot in (bplot_bfq, bplot_bdn, bplot_bfr, bplot_bpc):
        for patch, colour in zip(bplot['boxes'], colours["by-recording"]):
            patch.set_facecolor(colour)
    figure.suptitle("Plots by recording date")
    pdf.savefig(figure)
