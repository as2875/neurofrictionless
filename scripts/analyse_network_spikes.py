import datapackage
import datetime
import elephant
import h5fd.plot
import matplotlib
import matplotlib.pyplot as plt
import os
import quantities as qt
import random
from h5fd.plot import RECORDING_ATTEMPTS
from matplotlib.backends.backend_pdf import PdfPages

# paths
DATA_DIR = "../data/2020-02-21_fd/"
ACTIVITY_FIGURE_PATH = "../plots/network_analysis.pdf"
CUTOUTS_FIGURE_PATH = "../plots/network_spikes_cutouts.pdf"
SCATTER_FIGURE_PATH = "../plots/network_spikes_age.png"
AMPLITUDE_FIGURE_PATH = "../plots/network_spikes_amplitude.png"
EXAMPLE_FIGURE_PATH = "../plots/supplementary_figures/network_activity_example.png"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300

# parameters for analysis
THRESH = 0.25  # network spike threshold
BINW = 0.02  # bin width in seconds

recordings = ({"2539": {}, "2540": {}},
              {"2539": {}, "2540": {}},
              {"2539": {}, "2540": {}})

# construct time series
for file in data_files:
    package = datapackage.Package(file)
    _, channels, _ = h5fd.plot.extract_spike_trains(package,
                                                    qt.ms,
                                                    output_unit=qt.s)
    # determine which series the file is in
    replicate = package.descriptor["meta"]["MEA"]
    datestamp = package.descriptor["meta"]["date"]
    recording_date = datetime.date(int("20" + datestamp[:2]),
                                   int(datestamp[2:4]),
                                   int(datestamp[4:]))
    age = int(package.descriptor["meta"]["age"])
    if RECORDING_ATTEMPTS[0][0] <= recording_date <= RECORDING_ATTEMPTS[0][1]:
        if replicate == "2539":
            recordings[0]["2539"][age] = channels
        else:
            recordings[0]["2540"][age] = channels
    elif RECORDING_ATTEMPTS[1][0] <= recording_date <= RECORDING_ATTEMPTS[1][1]:
        if replicate == "2539":
            recordings[1]["2539"][age] = channels
        else:
            recordings[1]["2540"][age] = channels
    else:
        if replicate == "2539":
            recordings[2]["2539"][age] = channels
        else:
            recordings[2]["2540"][age] = channels

# analysis
# bin spikes
age_rate_l, age_amp_l, rate_l, amp_l = [], [], [], []
with PdfPages(ACTIVITY_FIGURE_PATH) as pdf_act, PdfPages(CUTOUTS_FIGURE_PATH) as pdf_cut:
    for i in range(len(recordings)):
        for replicate in sorted(recordings[i].keys()):
            for age in sorted(recordings[i][replicate].keys()):
                # bin
                labels = list(recordings[i][replicate][age].keys())
                spike_trains = [recordings[i][replicate][age][label] for label in labels]
                if not spike_trains:
                    continue
                binned_train = elephant.conversion.BinnedSpikeTrain(spike_trains,
                                                                    binsize=BINW*qt.s)
                meta = {"age": age,
                        "replicate": replicate,
                        "recording": i}
                ns = h5fd.plot.NetworkSpikes(binned_train,
                                             labels,
                                             meta=meta)
                ns.detect_spikes(THRESH)
                if ns.spike_cutouts:
                    age_rate_l.append(ns.meta["age"])
                    N = len(ns.spike_timestamps)
                    rate = N / ns.t_stop.rescale(qt.min)
                    rate_l.append(rate)
                    for j in range(len(ns.spike_cutouts)):
                        plt.plot(ns.spike_cutouts[j])
                        plt.title(ns.meta["replicate"] +
                                  " D" + str(ns.meta["age"]))
                        plt.xlabel("bin\ntimestamp=" +
                                   str(round(ns.spike_timestamps[j], 1)))
                        plt.ylabel("#spikes")
                        plt.tight_layout()
                        pdf_cut.savefig()
                        plt.close()
                        age_amp_l.append(ns.meta["age"])
                        amp = max(ns.spike_cutouts[j])
                        amp_l.append(amp)

                # plot
                figure, axes = plt.subplots()
                axes.plot(binned_train.bin_centers,
                          ns.network_activity,
                          "k",
                          lw=0.1)
                for ts in ns.spike_timestamps:
                    axes.plot((ts), (0), "rx")
                plt.title("D" + str(age) + " R" + replicate)
                plt.xlabel("time / s\n#channels=" + str(len(spike_trains)))
                plt.ylabel("#spikes in bin")
                plt.tight_layout()
                if i == 0 and replicate == "2540" and age == 34:
                    plt.savefig(EXAMPLE_FIGURE_PATH)
                pdf_act.savefig()
                plt.close()

# rate
plt.plot(age_rate_l, rate_l, ".")
plt.xlabel("age / DIV")
plt.ylabel("network spikes per min")
plt.tight_layout()
plt.savefig(SCATTER_FIGURE_PATH)
plt.close()

# amplitude
plt.plot(age_amp_l, amp_l, ".", alpha=0.1)
plt.xlabel("age / DIV")
plt.ylabel("number of spikes")
plt.tight_layout()
plt.savefig(AMPLITUDE_FIGURE_PATH)
plt.close()
