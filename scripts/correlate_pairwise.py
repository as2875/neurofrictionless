import datapackage
import dataflows
import datetime
import elephant
import h5fd.plot
import numpy
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import quantities as qt
from h5fd.plot import RECORDING_ATTEMPTS
from tqdm import tqdm

DATA_DIR = "../data/2020-02-21_fd/"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

# plotting parameters
FIGURE_PATH = "../plots/correlation_plots.pdf"
# CONTROL_FIGURE_PATH = "../plots/correlation_plots_randomised.pdf"
PACKAGE_PATH = "../plots/points/correlation_plots.zip"
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [6.69, 7.5]
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False

BINW = 0.5 * qt.s

print("Analysing data...")

age_l, corr_l, colours, err_l, empty = \
    ({"2539": ([], [], []), "2540": ([], [], [])} for i in range(5))

correlation_matrices, resource_names, dates, ages, \
replicates = [], [], [], [], []

for file in tqdm(data_files):
    # extract data
    package = datapackage.Package(file)
    mea = package.descriptor["meta"]["MEA"]
    age = package.descriptor["meta"]["age"]
    age = int(age)
    datestamp = package.descriptor["meta"]["date"]

    recording_date = datetime.date(int("20" + datestamp[:2]),
                                   int(datestamp[2:4]),
                                   int(datestamp[4:]))
    if RECORDING_ATTEMPTS[0][0] <= recording_date <= RECORDING_ATTEMPTS[0][1]:
        series = 0
    elif RECORDING_ATTEMPTS[1][0] <= recording_date <= RECORDING_ATTEMPTS[1][1]:
        series = 1
    else:
        series = 2

    _, channels, _ = h5fd.plot.extract_spike_trains(package,
                                                    qt.ms,
                                                    qt.s,
                                                    threshold=0.5*(1/qt.min))
    labels = list(channels.keys())
    trains = [channels[l] for l in labels]
    if len(trains) < 2:
        empty[mea][series].append(age)
        continue
    surr_trains = [elephant.spike_train_surrogates.randomise_spikes(t)[0]
                   for t in trains]

    # bin
    corr = numpy.zeros((len(trains), len(trains)))  # a square matrix
    surr_corr = numpy.zeros((len(trains), len(trains)))
    for i in range(len(trains)):
        for j in range(len(trains)):
            coeff = \
                elephant.spike_train_correlation.\
                spike_time_tiling_coefficient(trains[i],
                                              trains[j],
                                              dt=0.05*qt.s)
            assert coeff <= 1, "STTC > 1"
            corr[i, j] = coeff
            surr_coeff = \
                elephant.spike_train_correlation.\
                spike_time_tiling_coefficient(surr_trains[i],
                                              surr_trains[j],
                                              dt=0.05*qt.s)
            surr_corr[i, j] = surr_coeff

    corr_list = corr.tolist()
    for i in range(len(corr)):
        corr_list[i] = dict(zip(labels, corr[i]))
    correlation_matrices.append(corr_list)
    resource_names.append(datestamp + "_D" + str(age) + "_R" + mea)
    dates.append(datestamp)
    ages.append(age)
    replicates.append(mea)
    diag = numpy.diagonal(corr)
    assert (diag == numpy.ones(len(trains))).all()

    # matrix is symmetric, take upper triangle
    corr_triu = numpy.triu(corr, k=1)
    nonz = corr_triu.ravel()[numpy.flatnonzero(corr_triu)]
    corr_l[mea][series].append(nonz.tolist())

    # randomised trains
    # surr_corr_triu = numpy.triu(surr_corr, k=1)
    # surr_n = (surr_corr.shape[0] * (surr_corr.shape[1] - 1)) / 2
    # mean_surr_corr = numpy.sum(surr_corr_triu) / surr_n
    # surr_corr_l[mea][series].append(mean_surr_corr)
    # standard deviation
    # surr_nonz = surr_corr_triu.ravel()[numpy.flatnonzero(surr_corr_triu)]
    # surr_err = numpy.std(surr_nonz)
    # surr_err_l[mea][series].append(surr_err)

    age_l[mea][series].append(age)

# plot
print("Plotting...")
figure, axes = plt.subplots(3, 2,
                            sharex=True,
                            sharey=True)
axes = axes.flatten()
col = {0: "r", 1: "b", 2: "k"}

count = 0
for i in range(3):
    for mea in ("2539", "2540"):
        if i == 2:
            xlabel = mea
        else:
            xlabel = ""
        if mea == "2539":
            if i == 1:
                ylabel = "STTC\nR" + str(i + 1)
            else:
                ylabel = "R" + str(i + 1)
        else:
            ylabel = ""
        axes[count].set_xlabel(xlabel)
        axes[count].set_ylabel(ylabel)
        parts = axes[count].violinplot(corr_l[mea][i],
                                       age_l[mea][i],
                                       widths=1)
        for p in parts["bodies"]:
            p.set_facecolor(col[i])
        for m, data in zip(parts["cbars"].get_segments(), corr_l[mea][i]):
            coords = m[1]
            axes[count].text(coords[0],
                             coords[1] + 0.02,
                             str(len(data)),
                             fontsize=4.5,
                             ha="center")
        axes[count].plot(empty[mea][i],
                         numpy.zeros(len(empty[mea][i])),
                         "k*", markeredgewidth=0.2)
        axes[count].set_ylim([-0.1, 1])
        count += 1

figure.text(0.5, 0.02, "age / DIV", ha="center", va="center")
figure.tight_layout()
plt.savefig(FIGURE_PATH)
plt.close()

# figure, axes = plt.subplots()
# axes.set_xlabel("age / DIV")
# axes.set_ylabel("STTC")
# axes.scatter(age_l["2539"], surr_corr_l["2539"], c=colours["2539"], marker="s")
# axes.scatter(age_l["2540"], surr_corr_l["2540"], c=colours["2540"], marker="o")
# axes.errorbar(age_l["2539"], surr_corr_l["2539"], fmt="none",
#               yerr=surr_err_l["2539"], ecolor="k")
# axes.errorbar(age_l["2540"], surr_corr_l["2540"], fmt="none",
#               yerr=surr_err_l["2540"], ecolor="k")
# figure.tight_layout()
# plt.savefig(CONTROL_FIGURE_PATH)
# plt.close()

# export as data package
print("Exporting results...")
calls = [dataflows.update_resource("res_" + str(i),
                                   name=name,
                                   date=date,
                                   age=age,
                                   replicate=replicate)
         for i, name, date, age, replicate in
         zip(range(1, len(resource_names) + 1),
             resource_names,
             dates,
             ages,
             replicates)]
f = dataflows.Flow(
    *correlation_matrices,
    *calls,
    dataflows.dump_to_zip(PACKAGE_PATH)
)
f.process()
