# -*- coding: utf-8 -*-

import datapackage
import os
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import ListVector, FloatVector

DATA_DIR = "../data/2020-02-21_fd/"
data_files = [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)]

for file in data_files:
    package = datapackage.Package(file)
    spikes = [float(row[0])/1000
              for row in package.get_resource("spikes").read()]

    # buRst deteRction
    meaRtools = importr("meaRtools")
    spikes_vec = FloatVector(spikes)
    mi_par = ListVector({"beg_isi": 0.1,
                         "end_isi": 0.25,
                         "min_ibi": 0.3,
                         "min_durn": 0.05,
                         "min_spikes": 5})
    allb = meaRtools.mi_find_bursts(spikes_vec, mi_par)
    print(file)
    print("---")
    print(allb)
    print("===")