# -*- coding: utf-8 -*-

import datapackage
import numpy
import os
import matplotlib.pyplot as plt

DATA_DIR = ""
data_files = os.listdir(DATA_DIR)

age_pts = []
mean_isi_pts = []
rate_pts = []
N_pts = []

for file in data_files:
    # import package
    path = os.path.join(DATA_DIR, file)
    data = datapackage.Package(path)
    spikes = data.get_resource("spikes").read()
    spike_times = []
    for row in spikes:
        train_id = int(row[1])
        spike_time = float(row[0])
        try:
            spike_times[train_id].append(spike_time)
        except IndexError:
            spike_times.append([spike_time])
    spike_times.sort()
    spike_trains = data.get_resource("spike-trains").read()

    # Extract metadata
    age = data.descriptor["age"]

    # Compute summary statistics for each spike train
    for train in spike_times:
        N = len(train)
        if N > 1:
            rate = N/(train[-1] - train[0])
        else:
            continue
        isi = numpy.diff(train)
        mean_isi = numpy.mean(isi)
        mean_isi_pts.append(mean_isi)
        rate_pts.append(rate)
        N_pts.append(N)
        age_pts.append(age)

plt.plot(age_pts, mean_isi_pts, "k.", age_pts, rate_pts, "b.")