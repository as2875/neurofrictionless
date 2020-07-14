# Frictionless Data Project

## Overview

This is the repository for a project aiming to (i) evaluate the tools developed by Frictionless Data in a research context and (ii) analyse some new data provided by Kaiser Karim.

`h5fd` is a package containing code used by the scripts in `scripts`. `h5fd.converter.Hdf5FdConverter` is a class for converting between the HDF5 format specified in 

> Eglen *et al.* (2014) 'A data repository and analysis framework for spontaneous neural activity recordings in developing retina', *Gigascience*, 3, 1. Available at: <https://doi.org/10.1186/2047-217X-3-3>.

and a Frictionless Data Package described in `h5fd/datapackage.json`. `h5fd.converter.McHdf5Converter` converts from raw data in a format written by MC Datatool to HDF5.

`h5fd.plot` contains functions for extracting, plotting, and analysing the data in `data`.

`scripts` contains scripts for processing the data in `data`.

Further documentation can be found in the subdirectories.

## Evaluation

Bugs in my and others' code are recorded in the [Issues](https://github.com/as2875/neurofrictionless/issues). Problems with Frictionless Data also live here until they are reported. The [Wiki](https://github.com/as2875/neurofrictionless/wiki) has other thoughts on Frictionless Data.