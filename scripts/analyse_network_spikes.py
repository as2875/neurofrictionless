import datapackage
import datetime
import elephant
import h5fd.plot
import matplotlib.pyplot as plt
import neo
import os
import quantities as qt
from h5fd.plot import RECORDING_ATTEMPTS
from matplotlib.backends.backend_pdf import PdfPages

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/network_analysis.pdf"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

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
with PdfPages(FIGURE_PATH) as pdf:
    for recording in recordings:
        for replicate in sorted(recording.keys()):
            for age in sorted(recording[replicate].keys()):
                spike_trains = list(recording[replicate][age].values())
                if not spike_trains:
                    continue
                binned_train = elephant.conversion.BinnedSpikeTrain(spike_trains,
                                                                    binsize=0.01*qt.s)
                y = [sum(col) for col in binned_train.to_array().T]
                plt.plot(binned_train.bin_centers,
                         y,
                         "k",
                         lw=0.1)
                plt.title(replicate + " D" + str(age))
                plt.xlabel("time / s\n#channels=" + str(len(spike_trains)))
                plt.tight_layout()
                pdf.savefig()
                plt.close()
