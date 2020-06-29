# -*- coding: utf-8 -*-

import datapackage
import scipy.signal
import matplotlib.pyplot as plt

DATA_FILE = "170927_D20_2540.zip"

package = datapackage.Package(DATA_FILE)
for resource in package.resources:
    time, voltage = [], []
    for row in resource.read():
        time.append(row[0])
        voltage.append(row[1])
    peaks, _ = scipy.signal.find_peaks(voltage)
    plt.plot(voltage)
    plt.plot(peaks, [ voltage[peak] for peak in peaks ], "x")
