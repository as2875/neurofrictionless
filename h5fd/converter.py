# -*- coding: utf-8 -*-
"""
This module contains functions to convert MEA recordings of spikes from HDF5
to a Frictionless Data Package.
"""

import csv
import datapackage
import h5py
import itertools
import os
import pkg_resources
import re
import numpy as np


class BaseConverter:
    """A base class for converters in this module."""

    def __init__(self):
        self.formats = dict()


class Hdf5FdConverter(BaseConverter):
    """A class for converting from HDF5 to Frictionless and back."""

    def read(self, filename):
        """Read a file in either format."""
        # extract extension
        ext = os.path.splitext(filename)[1]

        if ext == ".h5":
            self.formats[".h5"] = h5py.File(filename, "r")
            self.formats[".zip"] = None
        elif ext == ".zip":
            # not implemented yet
            # of doubtful utility
            raise NotImplementedError()
        else:
            raise TypeError("File in unsupported format")

    def write(self, filename):
        """Write a file in either format."""
        # extract extension
        base = os.path.realpath(
            os.path.dirname(filename))
        ext = os.path.splitext(filename)[1]

        # if we haven't read anything, there is nothing to write
        assert self.formats, "Nothing to write"

        if self.formats[ext]:
            # if we already have the correct format, write immediately
            # not implemented yet
            raise NotImplementedError()
        else:
            if ext == ".zip":
                # convert from HDF5 to Frictionless
                # load data from HDF5 file
                s_count = list(self.formats[".h5"]["sCount"])
                spikes = list(self.formats[".h5"]["spikes"])
                if "names" in self.formats[".h5"].keys():
                    names = list(self.formats[".h5"]["names"])
                epos = list(self.formats[".h5"]["epos"])

                # set up data package
                datapackage_path = pkg_resources.resource_filename(
                    __package__,
                    "datapackage.json")
                package = datapackage.Package(
                    base_path=base,
                    descriptor=datapackage_path)

                # add metadata to data package descriptor
                for k, v in self.formats[".h5"]["meta"].items():
                    value = v[0].item()
                    if isinstance(value, bytes):
                        value = value.decode()
                    package.descriptor[k] = value

                package.commit()

                # extract resource names
                spike_trains_path = package.get_resource("spike-trains").source
                spikes_path = package.get_resource("spikes").source

                with open(spike_trains_path, "w", newline="") as spike_trains_file, open(spikes_path, "w", newline="") as spikes_file:
                    # initialise writers
                    spike_trains_writer = csv.writer(spike_trains_file)
                    spikes_writer = csv.writer(spikes_file)

                    # write headers
                    spike_trains_fields = [field.name for field in package.get_resource("spike-trains").schema.fields]
                    spike_trains_writer.writerow(spike_trains_fields)
                    spikes_fields = [field.name for field in package.get_resource("spikes").schema.fields]
                    spikes_writer.writerow(spikes_fields)

                    count = 0  # where in spikes we are
                    for i in range(len(s_count)):
                        # write to spike_trains.csv
                        if "names" in self.formats[".h5"].keys():
                            row = [i,
                                   names[i].decode(),
                                   epos[i][0],
                                   epos[i][1],
                                   s_count[i]]
                        else:
                            row = [i,
                                   "",
                                   epos[i][0],
                                   epos[i][1],
                                   s_count[i]]
                        spike_trains_writer.writerow(row)
                        for j in range(count, count + s_count[i]):
                            # write to spikes.csv
                            spikes_writer.writerow([spikes[j],
                                                    i])
                        count += s_count[i]

                # zip, zip
                package.save(filename)

                # remove csv files
                os.remove(spike_trains_path)
                os.remove(spikes_path)
                self.formats[".h5"].close()
            elif ext == ".h5":
                # convert from Frictionless to HDF5
                raise NotImplementedError()
            else:
                raise TypeError("Unsupported format")


class McHdf5Converter(BaseConverter):
    """A class for converting from MC Datatool files to HDF5."""

    def read(self, filename):
        ext = os.path.splitext(filename)[1]
        if ext != ".txt":
            raise TypeError("Unsupported format")
        with open(filename) as f:
            self.formats[ext] = f.read()

    def write(self, filename):
        # setup
        index_pattern = re.compile(r"(?<=Spikes \d )\d\d")
        whitespace_pattern = re.compile(r"\s+")

        # extract spike times from file
        channels = self.formats[".txt"].split("\n\n\n")
        channels = channels[1:]  # remove heading

        spikes = dict()
        t_stop = 0
        for channel in channels:
            waveforms = [spike.strip().split("\n")
                         for spike in channel.strip().split("\n\n")]
            # exclude empty channels
            if len(waveforms) <= 2:
                continue

            index = re.search(index_pattern, channel)
            index = index.group(0)
            spikes[index] = list()

            for wave in waveforms:
                spike_time = float(re.split(whitespace_pattern, wave[25])[0])
                if spike_time > t_stop:
                    t_stop = spike_time
                spikes[index].append(spike_time)

        assert spikes, "Recording is empty."

        electrodes = list(spikes.keys())
        trains = [spikes[e] for e in electrodes]

        with h5py.File(filename, "w") as hdf:
            spikes = list(itertools.chain(*trains))
            s_count = [len(train) for train in trains]
            epos = [(int(e[0]), int(e[1])) for e in electrodes]
            hdf.create_dataset("spikes", data=spikes)
            hdf.create_dataset("sCount", data=s_count)
            hdf.create_dataset("epos", data=epos)
            hdf.create_dataset("array", shape=(1,))
            hdf.create_group("meta")
            hdf.create_group("summary")
            hdf["summary"].create_dataset("N", data=[len(spikes)])
            hdf["summary"].create_dataset("duration", data=[t_stop])
