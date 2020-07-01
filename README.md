# Frictionless Data Project

This repository contains the package `h5fd`. `h5fd.converter.Hdf5FdConverter` is a class for converting between the HDF5 format specified in 

> Eglen *et al.* (2014) 'A data repository and analysis framework for spontaneous neural activity recordings in developing retina', *Gigascience*, 3, 1. Available at: <https://doi.org/10.1186/2047-217X-3-3>.

and a Frictionless Data Package described in `h5fd/datapackage.json`. `h5fd.converter.McHdf5Converter` converts from raw data in a format written by MC Datatool to HDF5.

Currently conversion in one direction is supported. Conversion in the other direction will only be implemented if required.

`scripts` contains myriad scripts for working with data.

`data` contains... data.