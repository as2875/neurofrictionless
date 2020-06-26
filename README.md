# Frictionless Data Project

This repository contains the package `h5fd`. `h5fd.converter.MEABurstConverter` is a class for converting between the HDF5 format specified in 

> Eglen *et al.* (2014) 'A data repository and analysis framework for spontaneous neural activity recordings in developing retina', *Gigascience*, 3, 1. Available at: <https://doi.org/10.1186/2047-217X-3-3>.

and a Frictionless Data Package described in `h5fd/datapackage.json`. Use it like so:

```
import h5fd.converter

c = h5fd.converter.MEABurstConverter()
c.read("mydata.h5")
c.write("mydata.zip")
```

Currently conversion in one direction is supported.

`scripts` contains myriad scripts for working with data.