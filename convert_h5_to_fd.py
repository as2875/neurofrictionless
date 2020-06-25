# -*- coding: utf-8 -*-

import h5fd.converter as h5fd

m = h5fd.MEABurstConverter()
m.read(r"C:\Users\sasha\Documents\burstanalysis\hiPSC_recordings\hiPSN_tc01_d12_spikes6sd.h5")
m.write("test.zip")