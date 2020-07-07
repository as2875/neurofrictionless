# -*- coding: utf-8 -*-
"""A module containing functions for plotting spike trains."""


def rasterplot(channels, axes, title):
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
    axes.set_xlabel("time / ms\n" + "#spikes = " + str(nspikes))
    axes.set_ylabel("channel")
    axes.set_title(title)

    y_offsets_map = dict(zip(labels, y_offsets))
    return y_offsets_map
