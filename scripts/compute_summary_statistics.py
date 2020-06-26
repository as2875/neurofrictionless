# -*- coding: utf-8 -*-

import datapackage
import numpy
import os
import matplotlib.pyplot as plt

DATA_DIR = r"C:\Users\sasha\Documents\fd_data"
data_files = os.listdir(DATA_DIR)

N_l = []
mean_isi_l = []
rate_l = []
age_l = []

for file in data_files:
    # import package
    path = os.path.join(DATA_DIR, file)
    data = datapackage.Package(path)
    spikes = data.get_resource("spikes").read()
    spike_times = [float(row[0]) for row in spikes]
    spike_times.sort()
    spike_trains = data.get_resource("spike-trains").read()
    
    # Compute summary statistics
    N = len(spike_times)
    rate = N/(spike_times[-1] - spike_times[0])
    isi = numpy.diff(spike_times)
    mean_isi = numpy.mean(isi)
    
    # Extract metadata
    div = data.descriptor["age"]
    age_l.append(div)
    
    # Print summary statistics
    N_l.append(N)
    rate_l.append(rate)
    mean_isi_l.append(mean_isi)

plt.plot(age_l, mean_isi_l, "k.", age_l, rate_l, "b.")