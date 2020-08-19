import datapackage
import dataflows
import datetime
import elephant
import h5fd.plot
import matplotlib
import matplotlib.pyplot as plt
import os
import quantities as qt
import warnings
from matplotlib.lines import Line2D
from h5fd.plot import RECORDING_ATTEMPTS
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

# suppress elephant warnings
warnings.filterwarnings("ignore", category=UserWarning,
                                  module="elephant")

# paths
DATA_DIR = "../data/2020-02-21_fd/"
ACTIVITY_FIGURE_PATH = "../plots/network_analysis.pdf"
CUTOUTS_FIGURE_PATH = "../plots/network_spikes_cutouts.pdf"
SCATTER_FIGURE_PATH = "../plots/network_spikes_scatter.pdf"
EXAMPLE_FIGURE_PATH = "../plots/supplementary_figures/network_activity_example.pdf"
PACKAGE_PATH = "../plots/points/network_analysis.zip"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

matplotlib.rcParams.update(matplotlib.rcParamsDefault)
matplotlib.rcParams["figure.dpi"] = 300
matplotlib.rcParams["figure.figsize"] = [6.69, 2.5]
matplotlib.rcParams["figure.constrained_layout.use"] = True
matplotlib.rcParams["font.size"] = 6.0

# parameters for analysis
THRESH = 0.25  # network spike threshold
BINW = 0.02  # bin width in seconds

recordings = ({"2539": {}, "2540": {}},
              {"2539": {}, "2540": {}},
              {"2539": {}, "2540": {}})

print("Reading data...")

# construct time series
for file in tqdm(data_files):
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
print("Analysing...")
age_rate_l, rate_l, colours = \
({"2539": [], "2540": []} for i in range(3))
age_amp_l, amp_l = [], []
with PdfPages(ACTIVITY_FIGURE_PATH) as pdf_act, PdfPages(CUTOUTS_FIGURE_PATH) as pdf_cut:
    for i in tqdm(range(len(recordings))):
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
                age_rate_l[replicate].append(ns.meta["age"])
                N = len(ns.spike_timestamps)
                rate = N / ns.t_stop.rescale(qt.min)
                rate_l[replicate].append(rate)
                if i == 0:
                    colours[replicate].append("r")
                elif i == 1:
                    colours[replicate].append("b")
                else:
                    colours[replicate].append("k")
                for j in range(len(ns.spike_cutouts)):
                    plt.plot(ns.spike_cutouts[j])
                    plt.title(ns.meta["replicate"] +
                              " D" + str(ns.meta["age"]))
                    plt.xlabel("bin\ntimestamp=" +
                               str(round(ns.spike_timestamps[j], 1)))
                    plt.ylabel("#spikes")
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
                if ns.threshold:
                    axes.axhline(ns.threshold, lw=0.2, color="r")
                for ts in ns.spike_timestamps:
                    axes.plot((ts), (0), "rx")
                plt.title("D" + str(age) + " R" + replicate)
                plt.xlabel("time / s\n#channels=" + str(len(spike_trains)))
                plt.ylabel("#spikes in bin")
                if i == 0 and replicate == "2540" and age == 34:
                    plt.savefig(EXAMPLE_FIGURE_PATH)
                pdf_act.savefig()
                plt.close()

figure, axes = plt.subplots(1, 2, sharex=True)
# rate
handles = [Line2D([0], [0], marker="s", color="grey", lw=0, label="2539"),
           Line2D([0], [0], marker="o", color="grey", lw=0, label="2540"),
           Line2D([0], [0], color="r", lw=5, label="R1"),
           Line2D([0], [0], color="b", lw=5, label="R2"),
           Line2D([0], [0], color="k", lw=5, label="R3")]
axes[0].legend(handles=handles, loc="upper left")
axes[0].scatter(age_rate_l["2539"], rate_l["2539"], c=colours["2539"], marker="s", s=9.0)
axes[0].scatter(age_rate_l["2540"], rate_l["2540"], c=colours["2540"], marker="o", s=9.0)
axes[0].set_xlabel("age / DIV")
axes[0].set_ylabel("frequency / min$^{-1}$")

# amplitude
ALPHA = 0.2
handles = [Line2D([0], [0], marker=".", color="g", lw=0, markeredgewidth=0,
           label="1", alpha=ALPHA),
           Line2D([0], [0], marker=".", color="g", lw=0, markeredgewidth=0,
           label="2", alpha=ALPHA*2),
           Line2D([0], [0], marker=".", color="g", lw=0, markeredgewidth=0,
           label="3", alpha=ALPHA*3),
           Line2D([0], [0], marker=".", color="g", lw=0, markeredgewidth=0,
           label="4", alpha=ALPHA*4),
           Line2D([0], [0], marker=".", color="g", lw=0, markeredgewidth=0,
           label="5", alpha=ALPHA*5)]
axes[1].legend(handles=handles, loc="upper left")
axes[1].plot(age_amp_l, amp_l, "g.", alpha=ALPHA, markeredgewidth=0)
axes[1].set_xlabel("age / DIV")
axes[1].set_ylabel("amplitude")
figure.savefig(SCATTER_FIGURE_PATH)

# export to datapackage
rate_table = [dict(age=age, rate=float(rate))
              for age, rate in zip(age_rate_l["2539"], rate_l["2539"])] + \
             [dict(age=age, rate=float(rate))
              for age, rate in zip(age_rate_l["2540"], rate_l["2540"])]
amp_table = [dict(age=age, amplitude=amp)
             for age, amp in zip(age_amp_l, amp_l)]
f = dataflows.Flow(
    rate_table,
    dataflows.update_resource("res_1", name="rate"),
    amp_table,
    dataflows.update_resource("res_2", name="amplitude"),
    dataflows.dump_to_zip(PACKAGE_PATH)
    )
f.process()
