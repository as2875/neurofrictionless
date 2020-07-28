import datapackage
import datetime
import elephant
import h5fd.plot
import itertools
import numpy
import os
import matplotlib
import matplotlib.pyplot as plt
import quantities as qt
from h5fd.plot import RECORDING_ATTEMPTS

DATA_DIR = "../data/2020-02-21_fd/"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

# plotting parameters
FIGURE_PATH = "../plots/correlation_plots.png"
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [10, 5]

BINW = 0.5 * qt.s

age_l, corr_l = [], []
err_l = []
colours = {"by-replicate": [], "by-recording": []}
for file in data_files:
    # extract data
    package = datapackage.Package(file)
    _, channels, _ = h5fd.plot.extract_spike_trains(package, qt.ms, qt.s)
    trains = list(channels.values())
    if len(trains) < 2:
        continue

    # bin
    corr = numpy.zeros((len(trains), len(trains)))  # a square matrix
    for i in range(len(trains)):
        for j in range(len(trains)):
            coeff = \
                elephant.spike_train_correlation.spike_time_tiling_coefficient(trains[i],
                                                                               trains[j])
            assert coeff <= 1, "STTC > 1"
            corr[i, j] = coeff

    # matrix is symmetric, take upper triangle
    corr_triu = numpy.triu(corr, k=1)
    n = (corr.shape[0] * (corr.shape[1] - 1)) / 2
    mean_corr = numpy.sum(corr_triu) / n
    corr_l.append(mean_corr)
    # standard error in the mean
    nonz = corr_triu.ravel()[numpy.flatnonzero(corr_triu)]
    err = numpy.std(nonz)
    err_l.append(err)
    # extract age
    age = int(package.descriptor["meta"]["age"])
    age_l.append(age)

    # which colour?
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

figure, axes = plt.subplots(1, 2, sharey=True)

axes[0].set_title("A")
axes[0].set_xlabel("age / DIV")
axes[0].set_ylabel("STTC")
axes[0].scatter(age_l, corr_l, c=colours["by-replicate"])
axes[0].errorbar(age_l, corr_l, fmt="none", yerr=err_l, ecolor="k")

axes[1].set_title("B")
axes[1].set_xlabel("age / DIV")
axes[1].set_ylabel("STTC")
axes[1].scatter(age_l, corr_l, c=colours["by-recording"])
axes[1].errorbar(age_l, corr_l, fmt="none", yerr=err_l, ecolor="k")

plt.savefig(FIGURE_PATH)
