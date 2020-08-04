# -*- coding: utf-8 -*-
import datapackage
import os


# filenames
FD_DIR = "../data/2020-02-21_fd/"
RAW_DIR = "../data/2020-02-21/"
files = os.listdir(FD_DIR)
fd_files = [os.path.join(FD_DIR, f) for f in files]
raw_files = []
for file in files:
    base = os.path.splitext(file)[0]
    path = os.path.join(RAW_DIR, base + ".txt")
    raw_files.append(path)

# compute number of spikes
for raw, fd in zip(raw_files, fd_files):
    with open(raw) as f:
        lines = f.readlines()
    # +1 might not be needed on Unix
    active_channels_raw = 0
    for i in range(len(lines) - 1):
        if lines[i] == "[ms]        \t[µV]        \t            \n" and \
          lines[i+1] != "\n":
            active_channels_raw += 1
    spikes_raw = (len(lines) - 60 * 4 - 2 + 1 + active_channels_raw) / 76
    package = datapackage.Package(fd)
    spikes_fd = len(package.get_resource("spikes").read())
    active_channels_fd = len(package.get_resource("spike-trains").read())
    assert spikes_raw == spikes_fd, "Difference in number of spikes in file " \
        + raw
    assert active_channels_raw == active_channels_fd, "Difference in number of\
        active channels in file " + raw
