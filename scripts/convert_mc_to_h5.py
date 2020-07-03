# -*- coding: utf-8 -*-

import h5fd.converter
import os

SOURCE_DIR = "../data/2020-02-21/"
TARGET_DIR = "../data/2020-02-21_hdf5/"

data_files = [file for file in os.listdir(SOURCE_DIR) if file.endswith(".txt")]
m = h5fd.converter.McHdf5Converter()

for file in data_files:
    path = os.path.join(SOURCE_DIR, file)
    m.read(path)
    base = os.path.splitext(file)[0]
    m.write(os.path.join(TARGET_DIR, base + ".h5"))
