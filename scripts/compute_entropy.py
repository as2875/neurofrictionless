# -*- coding: utf-8 -*-

import os
import elephant
import datapackage
import h5fd.plot
import quantities as qt
import scipy.stats
import matplotlib.pyplot as plt
import warnings
from tqdm import tqdm

# suppress elephant warnings
warnings.filterwarnings("ignore", category=UserWarning,
                                  module="elephant")

DATA_DIR = "../data/2020-02-21_fd/"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

age_l, entropy_l = [], []
for file in tqdm(data_files):
    package = datapackage.Package(file)
    age = package.descriptor["meta"]["age"]
    _, channels, _ = h5fd.plot.extract_spike_trains(package,
                                                    qt.ms,
                                                    qt.s,
                                                    threshold=10*(1/qt.min))
    if not channels:
        continue
    hist = elephant.statistics.time_histogram(channels.values(),
                                              binsize=500*qt.ms)
    entropy = scipy.stats.entropy(hist.T[0])
    age_l.append(age)
    entropy_l.append(entropy)

plt.plot(age_l, entropy_l, "k.")
plt.xlabel("age / DIV")
plt.ylabel("entropy")
