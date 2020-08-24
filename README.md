# Frictionless Data Project

[![Build Status](https://travis-ci.com/as2875/neurofrictionless.svg?token=ErkgFJZ5ht5B2sjWsfq9&branch=master)](https://travis-ci.com/as2875/neurofrictionless)

## Overview

This is the repository for a project aiming to (i) evaluate the tools developed by Frictionless Data in a research context and (ii) analyse some new data provided by Kaiser Karim.

The bulk of the data analysis is done by Python scripts located in the `scripts` directory. They rely on a Python package, `h5fd`, which includes code for converting between formats (`h5fd.converter`) and miscellaneous data analysis functions (somewhat misleadlingly called `h5fd.plot`).

`tests` contains benchmarks and sanity checks.

Descriptions of what scripts do and what plots represent can be found in the relevant subdirectories.

## Data conversion

The raw data were provided in a format written by MC_DataTool. `scripts/convert_mc_to_h5.py` converts the raw data to an HDF5 format specified in

> Eglen *et al.* (2014) 'A data repository and analysis framework for spontaneous neural activity recordings in developing retina', *Gigascience*, 3, 1. Available at: <https://doi.org/10.1186/2047-217X-3-3>.

`scripts/convert_h5_to_fd.py` converts this HDF5 data into a Frictionless Data format.

## Setup

1. Install R and meaRtools.
2. Clone the repository.
3. You may find it convenient to set up a virtual environment.
    - Install the `virtualenv` package (`sudo apt install python3-virtualenv` on Ubuntu).
    - `virtualenv venv`
    - `source venv/bin/activate`
4. Add the repository to `PYTHONPATH`. On Linux, run `export PYTHONPATH=/path/to/repository`.
5. Run `pip install -r requirements.txt`.

## Running the analysis

1. `cd` into the repository.
2. `make clean` for a fresh start.
2. `make convert` to convert the raw data into HDF5 and Frictionless formats.
3. `make all` to generate all figures and data packages with results of select analyses.

## Evaluation

Bugs in my and others' code are recorded in the [Issues](https://github.com/as2875/neurofrictionless/issues). Problems with Frictionless Data also live here until they are reported. The [Wiki](https://github.com/as2875/neurofrictionless/wiki) has other thoughts on Frictionless Data.
