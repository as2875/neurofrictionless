# -*- coding: utf-8 -*-

import datapackage
import os
import re

SOURCE_FILENAME = "170927_D20_2540.txt"
basename = os.path.splitext(SOURCE_FILENAME)[0]
index_pattern = re.compile("(?<=Spikes 1 )\d+")

with open(SOURCE_FILENAME) as f:
    data = f.read()

channels = data.split("\n\n\n")
channels.pop(0) # remove heading

csv_files = []
for channel in channels:
    lines = channel.strip().split("\n")
    if len(lines) <= 2:
        continue
    
    index = re.search(index_pattern, channel)
    index = index.group(0)
    
    filename = basename + "_CHAN" + index + ".csv"
    csv_files.append(filename)
    lines.pop(0)
    lines.pop(0)
    lines.insert(0, "time\tvoltage\tunit")
    with open(filename, "w") as f:
        f.write("\n".join(lines))

package = datapackage.Package()
package.infer("*.csv")
package.save(basename + ".zip")
for file in csv_files:
    os.remove(file)