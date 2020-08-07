# Plots

All plots are generated from data in a Frictionless format, other than `raster_plots.pdf`, which uses the raw data.

`points` contains the output of select scripts in Frictionless format. `supplementary_figures` contains examples from some of the multipage plots.

| Filename | Description | Script |
| --- | --- | --- |
| `burst_boxplots` | A series of box plots summarising burst behaviour. | `compute_burst_statistics.py` |
| `burst_plots` | A raster plot with bursts marked on it. | `detect_bursts.py` |
| `correlation_plots` | A plot of mean STTC against age. | `correlate_pairwise.py` |
| `correlation_plots` | A plot of mean STTC of spike trains after randomly repositioning spikes against age. | `correlate_pairwise.py` |
| `development_plots*` | A plot of various summary statistics (firing rate, number of spikes) against age | `compute_summary_statistics.py` |
| `file_size_plot` | A plot of file size against number of spikes. | `file_size_benchmark.py` |
| `logisi_plots` | Contains a histogram, for every channel in every recording, of the (natural) log of the interspike interval. | `compute_isi_distribution.py` |
| `raster_plots` | Contains a raster plot, diagram of active channels, and plot of instantaneous firing rate, for every recording. | `process_mcdatatool.py` |
| `network_analysis` | Contains plots of the number of spikes in each bin. | `analyse_network_spikes.py` |
| `network_spikes_cutouts` | Contains cutouts of network spikes. | `analyse_network_spikes.py` |
| `network_spikes_age` | A plot of rate of network spike occurrence against age. | `analyse_network_spikes.py` |
| `network_spikes_amplitude` | A plot of amplitude of network spikes against age. | `analyse_network_spikes.py` |
