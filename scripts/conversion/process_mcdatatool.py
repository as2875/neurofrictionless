# -*- coding: utf-8 -*-

import datapackage
import os
import re

SOURCE_FILENAME = "170927_D20_2540.txt"
basename = os.path.splitext(SOURCE_FILENAME)[0]
exclude_pattern = re.compile("^\D")  # line begins with a character that is not a digit

with open(SOURCE_FILENAME) as f:
    lines = [line.replace(' ', '') for line in f.readlines() if line.strip()
             and not re.match(exclude_pattern, line)]
lines.insert(0, 'time\tvoltage\tunit\n')  # insert headers

with open(basename + ".csv", "w") as f:
    f.writelines(lines)

package = datapackage.Package()
package.infer("*.csv")
package.save(basename + ".zip")