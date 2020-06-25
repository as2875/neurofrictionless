# -*- coding: utf-8 -*-
"""
This module contains functions to convert MEA recordings of spikes from HDF5
to a Frictionless Data Package.
"""

import csv
import datapackage
import h5py
import os
import pkg_resources


class MEABurstConverter:
    """A class for converting from HDF5 to Frictionless and back."""

    def __init__(self):
        self.formats = {}

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
                names = list(self.formats[".h5"]["names"])
                epos = list(self.formats[".h5"]["epos"])

                # set up data package
                datapackage_path = \
                    pkg_resources.resource_filename(__package__, "datapackage.json")
                package = datapackage.Package(
                    base_path=base,
                    descriptor=datapackage_path)

                with open(package.get_resource("spike-trains").source, "w", newline="") as spike_trains_file, open(package.get_resource("spikes").source, "w", newline="") as spikes_file:

                    # initialise writers
                    spike_trains_writer = csv.writer(spike_trains_file)
                    spikes_writer = csv.writer(spikes_file)

                    # write headers
                    spike_trains_fields = [ field.name for field in package.get_resource("spike-trains").schema.fields ]
                    spike_trains_writer.writerow(spike_trains_fields)
                    spikes_fields = [ field.name for field in package.get_resource("spikes").schema.fields ]
                    spikes_writer.writerow(spikes_fields)

                    count = 0  # where in spikes we are
                    for i in range(len(s_count)):
                        # write to spike_trains.csv
                        spike_trains_writer.writerow([i,
                                                     names[i].decode(),
                                                     epos[0][i],
                                                     epos[1][i],
                                                     s_count[i]])
                        for j in range(count, count + s_count[i]):
                            spikes_writer.writerow([spikes[j],
                                                    i])
                        count += s_count[i]

                # make a data package
                package.save(filename)
                self.formats[".zip"] = package

                # remove folder
                # shutil.rmtree(data_dir)

            elif ext == ".h5":
                # convert from Frictionless to HDF5
                raise NotImplementedError()