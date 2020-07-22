# Plots

All plots are generated from data in a Frictionless format, other than `raster_plots.pdf`, which uses the raw data.

| Filename | Description | Script |
| --- | --- | --- |
| `burst_boxplots.png` | A series of box plots summarising burst behaviour. | `compute_burst_statistics.py` |
| `burst_plots.pdf` | A raster plot with bursts marked on it. | `detect_bursts.py` |
| `correlation_plots.pdf` | A plot of mean correlation against age. | `correlate_pairwise.py` |
| `development_plots.pdf` | A plot of various summary statistics (firing rate, number of spikes) against age | `compute_summary_statistics.py` |
| `logisi_plots.pdf` | Contains a histogram, for every channel in every recording, of the (natural) log of the interspike interval. | `compute_isi_distribution.py` |
| `raster_plots.pdf` | Contains a raster plot, diagram of active channels, and plot of instantaneous firing rate, for every recording. | `process_mcdatatool.py` |
| `network_analysis.pdf` | Contains plots of the number of spikes in each bin. | `analyse_network_spikes.py` |
| `network_spikes_cutouts.pdf` | Contains cutouts of network spikes. | `analyse_network_spikes.py` |
| `network_spikes_age.pdf` | A plot of rate of network spike occurrence against age. | `analyse_network_spikes.py` |