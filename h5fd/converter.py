# -*- coding: utf-8 -*-
"""
This module contains functions to convert MEA recordings of spikes from HDF5
to a Frictionless Data Package.
"""

import datapackage
import dataflows
import h5py
import itertools
import numpy
import os
import re


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
        if ext != ".h5" and ext != ".zip":
            raise TypeError("Unsupported format:", ext)

        if ext == ".h5":
            with h5py.File(filename, "r") as f:
                self.s_count = numpy.array(f["sCount"])
                self.spikes = numpy.array(f["spikes"])
                if "names" in f.keys():
                    self.names = numpy.array(f["names"])
                else:
                    self.names = None
                self.epos = numpy.array(f["epos"])
                self.meta = dict()
                for k, v in f["meta"].items():
                    value = v[0].item()
                    if isinstance(value, bytes):
                        value = value.decode()
                    self.meta[k] = value
        else:
            self.formats[".zip"] = datapackage.Package(filename)

    def write(self, filename):
        """Write a file in either format."""
        # extract extension
        ext = os.path.splitext(filename)[1]
        assert ext == ".zip" or ext == ".h5", "Unsupported format"

        if ext == ".zip":
            # convert from HDF5 to Frictionless
            flow = dataflows.Flow(
                self._spikes(),
                self._trains(),
                dataflows.update_resource("res_1", name="spikes"),
                dataflows.update_resource("res_2", name="spike-trains"),
                dataflows.update_package(meta=self.meta),
                dataflows.dump_to_zip(filename)
                )
            flow.process()

        elif ext == ".h5":
            # convert from Frictionless to HDF5
            assert ".zip" in self.formats.keys(),\
                "No Frictionless to convert from"
            package = self.formats[".zip"]  # for convenience
            spikes = [float(row["time"]) for row in
                      package.get_resource("spikes").read(keyed=True)]
            name, epos, s_count = [], [], []
            for train in package.get_resource("spike-trains").read(keyed=True):
                if train["name"]:
                    name.append(str.encode(train["name"]))
                epos.append((float(train["epos-x"]), float(train["epos-y"])))
                s_count.append(int(train["sCount"]))
            with h5py.File(filename, "w") as hdf:
                hdf.create_dataset("spikes", data=spikes)
                hdf.create_dataset("sCount", data=s_count)
                hdf.create_dataset("epos", data=epos)
                hdf.create_group("meta")
                for k, v in package.descriptor["meta"].items():
                    value = v
                    if isinstance(value, str):
                        value = str.encode(value)
                    hdf["meta"].create_dataset(k, data=[value])
        else:
            raise TypeError("Unsupported format")

    def _trains(self):
        for i in range(len(self.s_count)):
            # write to spike_trains.csv
            if self.names:
                row = {"spike-train-index": i,
                       "name": self.names[i].decode(),
                       "epos-x": self.epos[0][i],
                       "epos-y": self.epos[1][i],
                       "sCount": self.s_count[i]}
            else:
                row = {"spike-train-index": i,
                       "name": "",
                       "epos-x": self.epos[0][i],
                       "epos-y": self.epos[1][i],
                       "sCount": self.s_count[i]}
            yield row

    def _spikes(self):
        count = 0  # where in spikes we are
        for i in range(len(self.s_count)):
            for j in range(count, count + self.s_count[i]):
                # write to spikes.csv
                row = {"time": self.spikes[j],
                       "spike-train-index": i}
                yield row
            count += self.s_count[i]


class McHdf5Converter(BaseConverter):
    """A class for converting from MC Datatool files to HDF5."""

    def read(self, filename):
        ext = os.path.splitext(filename)[1]
        self.basename = os.path.splitext(os.path.split(filename)[1])[0]
        if ext != ".txt":
            raise TypeError("Unsupported format")
        with open(filename) as f:
            self.formats[ext] = f.read()
            self.formats[ext] = self.formats[ext][30:]  # chew off header

    def write(self, filename):
        assert filename.endswith(".h5"), "Filename must end with '.h5'"

        # setup
        index_pattern = re.compile(r"(?<=Spikes \d )\d\d")
        whitespace_pattern = re.compile(r"\s+")
        age_pattern = re.compile(r"(?<=D)\d+")

        # extract spike times from file
        channels = self.formats[".txt"].split("\n\n\n")

        spikes = dict()
        t_stop = 0
        for channel in channels:
            waveforms = [spike.strip().split("\n")
                         for spike in channel.strip().split("\n\n")]
            # chew off headers
            waveforms[0] = waveforms[0][2:]

            # exclude empty channels
            if len(waveforms[0]) == 0:
                continue

            index = re.search(index_pattern, channel)
            index = index.group(0)
            spikes[index] = list()

            for wave in waveforms:
                spike_time = float(re.split(whitespace_pattern, wave[25])[0])
                if spike_time > t_stop:
                    t_stop = spike_time
                spikes[index].append(spike_time)

        electrodes = list(spikes.keys())
        trains = [spikes[e] for e in electrodes]

        with h5py.File(filename, "w") as hdf:
            spikes = list(itertools.chain(*trains))
            s_count = [len(train) for train in trains]
            epos = [[], []]
            for e in electrodes:
                epos[0].append(int(e[0]))
                epos[1].append(int(e[1]))
            hdf.create_dataset("spikes", data=spikes)
            hdf.create_dataset("sCount", data=s_count)
            hdf.create_dataset("epos", data=epos)
            hdf.create_dataset("array", shape=(1,))

            hdf.create_group("meta")
            date = str.encode(self.basename[:6])
            age = int(re.search(age_pattern, self.basename).group(0))
            mea = str.encode(self.basename[-4:])
            hdf["meta"].create_dataset("date", data=[date])
            hdf["meta"].create_dataset("age", data=[age])
            hdf["meta"].create_dataset("MEA", data=[mea])

            hdf.create_group("summary")
            hdf["summary"].create_dataset("N", data=[len(spikes)])
            hdf["summary"].create_dataset("duration", data=[t_stop])
