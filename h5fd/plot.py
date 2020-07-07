# -*- coding: utf-8 -*-
"""A module containing functions for plotting spike trains."""

import neo


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


def extract_spike_trains(package, unit):
    """
    Extract spike trains from a Frictionless data package.

    Parameters
    ----------
    package : datapackage.Package
        Data package from which to extract spikes.
    unit : quantities.unitquantity.UnitTime
        Unit of time in file.

    Returns
    -------
    Dictionary of channels and stopping time.

    """
    spikes, channels, t_stop = [], {}, 0
    for row in package.get_resource("spikes").read(keyed=True):
        spike_time = float(row["time"])
        spikes.append(spike_time)
        index = row["spike-train-index"]
        if index not in channels.keys():
            channels[index] = []
        channels[index].append(spike_time)
        if spike_time > t_stop:
            t_stop = spike_time

    spikes = neo.SpikeTrain(spikes * unit, t_stop)
    for k in channels.keys():
        channels[k] = neo.SpikeTrain(channels[k] * unit, t_stop)

    return spikes, channels, t_stop
