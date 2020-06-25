# -*- coding: utf-8 -*-

import h5fd.converter
import os

DATA_DIR = r"C:\Users\sasha\Documents\burstanalysis\hiPSC_recordings"

data_files = os.listdir(DATA_DIR)
m = h5fd.converter.MEABurstConverter()

for file in data_files:
    path = os.path.join(DATA_DIR, file)
    m.read(path)
    base = os.path.splitext(file)[0]
    m.write(base + ".zip")