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
matplotlib.rcParams["figure.figsize"] = [5, 5]

BINW = 0.5 * qt.s

age_l, corr_l, colours, err_l = ({"2539": [], "2540": []} for i in range(4))
for file in data_files:
    # extract data
    package = datapackage.Package(file)
    mea = package.descriptor["meta"]["MEA"]
    _, channels, _ = h5fd.plot.extract_spike_trains(package, qt.ms, qt.s)
    trains = list(channels.values())
    if len(trains) < 2:
        continue

    # bin
    corr = numpy.zeros((len(trains), len(trains)))  # a square matrix
    for i in range(len(trains)):
        for j in range(len(trains)):
            coeff = \
                elephant.spike_train_correlation.\
                spike_time_tiling_coefficient(trains[i],
                                              trains[j],
                                              dt=0.05*qt.s)
            assert coeff <= 1, "STTC > 1"
            corr[i, j] = coeff

    # matrix is symmetric, take upper triangle
    corr_triu = numpy.triu(corr, k=1)
    n = (corr.shape[0] * (corr.shape[1] - 1)) / 2
    mean_corr = numpy.sum(corr_triu) / n
    corr_l[mea].append(mean_corr)
    # standard error in the mean
    nonz = corr_triu.ravel()[numpy.flatnonzero(corr_triu)]
    err = numpy.std(nonz)
    err_l[mea].append(err)
    # extract age
    age = int(package.descriptor["meta"]["age"])
    age_l[mea].append(age)

    datestamp = package.descriptor["meta"]["date"]
    recording_date = datetime.date(int("20" + datestamp[:2]),
                                   int(datestamp[2:4]),
                                   int(datestamp[4:]))
    if RECORDING_ATTEMPTS[0][0] <= recording_date <= RECORDING_ATTEMPTS[0][1]:
        colours[mea].append("r")
    elif RECORDING_ATTEMPTS[1][0] <= recording_date <= RECORDING_ATTEMPTS[1][1]:
        colours[mea].append("b")
    else:
        colours[mea].append("k")

figure, axes = plt.subplots()

axes.set_xlabel("age / DIV")
axes.set_ylabel("STTC")
axes.scatter(age_l["2539"], corr_l["2539"], c=colours["2539"], marker="s")
axes.scatter(age_l["2540"], corr_l["2540"], c=colours["2540"], marker="o")
axes.errorbar(age_l["2539"], corr_l["2539"], fmt="none", yerr=err_l["2539"], ecolor="k")
axes.errorbar(age_l["2540"], corr_l["2540"], fmt="none", yerr=err_l["2540"], ecolor="k")
plt.savefig(FIGURE_PATH)
