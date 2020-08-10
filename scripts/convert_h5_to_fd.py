# -*- coding: utf-8 -*-

import h5fd.converter
import os
from tqdm import tqdm

SOURCE_DIR = "../data/2020-02-21_hdf5/"
TARGET_DIR = "../data/2020-02-21_fd/"

data_files = [file for file in os.listdir(SOURCE_DIR) if file.endswith(".h5")]
m = h5fd.converter.Hdf5FdConverter()

for file in tqdm(data_files):
    path = os.path.join(SOURCE_DIR, file)
    m.read(path)
    base = os.path.splitext(file)[0]
    m.write(os.path.join(TARGET_DIR, base + ".zip"))
