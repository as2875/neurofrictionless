# -*- coding: utf-8 -*-
"""
Plot the number of spikes against the file size

@author: Alexander Shtyrov
"""


import datapackage
import os
import matplotlib.pyplot as plt

DATA_DIR = "../data/2020-02-21_fd/"
FIGURE_PATH = "../plots/file_size_plot.png"
data_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)]

N_l, size_l = [], []
for file in data_files:
    package = datapackage.Package(file)
    n = len(package.get_resource("spikes").read())
    size = os.path.getsize(file)
    N_l.append(n)
    size_l.append(size)

plt.plot(N_l, size_l, "k.")
plt.xlabel("number of spikes")
plt.ylabel("file size / bytes")
plt.title("$n=" + str(len(data_files)) + "$")
plt.savefig(FIGURE_PATH)
