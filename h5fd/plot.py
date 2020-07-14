# -*- coding: utf-8 -*-
"""A module containing functions for plotting spike trains."""

import datetime
import elephant.statistics
import neo
import numpy
import quantities as qt

RECORDING_ATTEMPTS = [(datetime.date(2017, 9, 15), datetime.date(2017, 10, 13)),
                      (datetime.date(2018, 1, 22), datetime.date(2018, 2, 19)),
                      (datetime.date(2018, 3, 28), datetime.date(2018, 5, 4))]


class NetworkSpikes:
    """Represents a series of network spikes."""

    def __init__(self, array, rows, bin_centres, meta=None):
        self.array = array  # each row is a spike train, each column is a bin
        self.network_activity =\
            numpy.array([sum(col) for col in array.T])  # sum each column
        self.active_channels = self.array.shape[0]  # number of rows in array
        self.rows = rows  # channel each row originates from
        self.meta = meta  # metadata
        self.bin_centres = bin_centres
        self.binw = self.bin_centres[1] - self.bin_centres[0]

    def detect_spikes(self, threshold):
        self.spike_timestamps = []
        self.spike_cutouts = []

        if self.active_channels < 8:
            return

        iterator = iter(range(len(self.network_activity)))
        for i in iterator:
            if self.network_activity[i] > threshold * self.active_channels:
                self.spike_timestamps.append(self.bin_centres[i])
                num_bins = ((150 * qt.ms) / self.binw).rescale(qt.dimensionless)
                num_bins = int(num_bins)
                cutout = self.network_activity[i - num_bins:i + num_bins]
                self.spike_cutouts.append(cutout)
                # skip forward 30 bins
                try:
                    for j in range(num_bins):
                        next(iterator)
                except StopIteration:
                    break


def rasterplot(channels, axes, title, unit):
    """
    Produce a raster plot of a spike train on a set of axes.

    Parameters
    ----------
    channels : dict
        A dictionary of spike trains. Keys are channel labels, values are
        lists of spikes.
    axes : matplotlib.axes.Axes
        Set of axes to plot on.
    title : str
        Figure title.
    unit : str
        Units of time to include on x-axis.

    Returns
    -------
    Dictionary mapping channels to offsets on y axis or None.

    """
    if not channels:
        axes.set_xlim((0, 2))
        axes.set_ylim((0, 2))
        axes.set_axis_off()
        axes.set_title(title)
        axes.text(1, 1, "no spikes", ha="center")
        return

    labels = list(channels.keys())

    events, nspikes = [], 0
    for label in labels:
        events.append(channels[label])
        nspikes += len(channels[label])

    y_offsets = list(range(len(labels)))
    axes.eventplot(events,
                   linelengths=0.75,
                   lineoffsets=y_offsets,
                   color="black",
                   lw=0.2)
    axes.set_yticks(y_offsets)
    axes.set_yticklabels(labels)
    axes.set_xlabel("time / " + unit + "\n" + "#spikes = " + str(nspikes))
    axes.set_ylabel("channel")
    axes.set_title(title)

    y_offsets_map = dict(zip(labels, y_offsets))
    return y_offsets_map


def extract_spike_trains(package,
                         input_unit,
                         output_unit=None,
                         threshold=None):
    """
    Extract spike trains from a Frictionless data package.

    Parameters
    ----------
    package : datapackage.Package
        Data package from which to extract spikes.
    input_unit : quantities.unitquantity.UnitTime
        Unit of time in file.
    output_unit : quantities.unitquantity.UnitTime
        Unit of time to rescale time of spike train to. t_stop not rescaled.
    threshold : quantities.Quantity
        Channels with a firing rate lower than the threshold are excluded.

    Returns
    -------
    List of channels, dictionary of channels, stopping time.

    """
    spikes, channels, t_stop = [], {}, 0
    for row in package.get_resource("spikes").read(keyed=True, relations=True):
        spike_time = float(row["time"])
        spikes.append(spike_time)
        index = row["spike-train-index"]["epos-x"] + \
                row["spike-train-index"]["epos-y"]
        if index not in channels.keys():
            channels[index] = []
        channels[index].append(spike_time)
        if spike_time > t_stop:
            t_stop = spike_time

    spikes = neo.SpikeTrain(spikes * input_unit, t_stop)
    t_stop = t_stop * input_unit
    if output_unit:
        spikes = spikes.rescale(output_unit)
        t_stop = t_stop.rescale(output_unit)

    channels_filtered = {}
    for k in channels.keys():
        channels[k] = neo.SpikeTrain(channels[k] * input_unit, t_stop)
        fr = elephant.statistics.mean_firing_rate(channels[k])
        if threshold and fr < threshold:
            continue
        channels_filtered[k] = channels[k]
        if output_unit:
            channels_filtered[k] = channels_filtered[k].rescale(output_unit)

    return spikes, channels_filtered, t_stop
