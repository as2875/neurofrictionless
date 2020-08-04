# -*- coding: utf-8 -*-
"""
Benchmarks for Frictionless Data.

@author: Alexander Shtyrov
"""


import timeit

hd5_setup = \
    """
import h5py
import numpy

def num_spikes_from_hd5(path):
    with h5py.File(path, "r") as hdf:
        spikes = numpy.array(hdf["spikes"])
        return len(spikes)
"""

fd_setup = \
    """
import datapackage

def num_spikes_from_fd(path):
    package = datapackage.Package(path)
    spikes = package.get_resource("spikes")
    return len(spikes.read())
"""

NUM = 10
# HDF5
durn = timeit.timeit("num_spikes_from_hd5('C57_TC191_G2CEPHYS1_DIV21_B.h5')",
                     setup=hd5_setup,
                     number=NUM)
print("HDF5:", durn/NUM, "s")

# Frictionless
durn = timeit.timeit("num_spikes_from_fd('C57_TC191_G2CEPHYS1_DIV21_B.zip')",
                     setup=fd_setup,
                     number=NUM)
print("FD:  ", durn/NUM, "s")